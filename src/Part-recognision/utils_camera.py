from ids_peak import ids_peak
from ids_peak_ipl import ids_peak_ipl
from ids_peak import ids_peak_ipl_extension
import cv2
import os
import sys
import threading
from datetime import datetime
import time
from collections import deque

VERSION = "1.2.0"
FPS_LIMIT = 30

class Camera:
    _instance = None  # Static instance variable to store the singleton

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Camera, cls).__new__(cls)
            cls._instance.is_initialized = False
            #cls._instance.__initialize_camera__()
        return cls._instance
    
    def __initialize_camera__(self):
        # Initialize variables
        self.__setup_camera_variables__()

        # Start to initialize camera
        print('Now the camera is initialized.')

        # initialize live_image_thread
        self.live_image_thread = threading.Thread(target=self.store_live_image)
        self.live_image_thread.daemon = True

        # initialize peak library
        ids_peak.Library.Initialize()

        # Try to connect to the camera, until successfull
        while not self.__try_connect__():
            # Connection failed
            print("Connection to camera failed. Try again in 5 seconds.")

            time.sleep(5)

        # Connection successfull
        print("Camera initialized successfully.")
        self.connected = True

        # Start the live_image_thread if connection was successfull
        self.live_image_thread.start()
        self.live_image_condition = threading.Condition()

    def __try_connect__(self):
        try: 
            # Try to connect
            if self.__open_device() and self.__start_acquisition():
                return True
            else:
                return False
        except Exception as e:
            print(f"Camera initialization error: {e}")

            return False
        
    def __setup_camera_variables__(self):
        self.__device = None
        self.__remote_device = None
        self.__datastream = None

        self.__nodemap_remote_device = None
        self.__payload_size = 0
        self.__buffer_count_max = 0

        self.__acquisition_running = False

        # initialize the variables for live_image_thread
        self.live_image = None  # New instance variable for storing the newest live image
        self.running = True
        self.connected = False

        # initialize ring buffer for motion trigger
        self.small_images_buffer = deque(maxlen=20)  # Ring buffer for small images
        self.buffer_lock = threading.Lock()  # Lock for ring buffer

    def start_camera(self):
        # Start the initialisation of the camera
        if not self.is_initialized:
            self.__initialize_camera__()
            self.is_initialized = True

    def stop_camera(self):
        # Stop the camera connection
        self.__destroy_all

    def __del__(self):
        self.__destroy_all()

    def __destroy_all(self):
        # Stop acquisition
        self.__stop_acquisition()

        # Close thread
        self.running = False
        if self.live_image_thread.is_alive():
            self.live_image_thread.join()

        # Close device and peak library
        self.__close_device()
        ids_peak.Library.Close()

    def __open_device(self):
        try:
            print('Try to open device.')

            # Create instance of the device manager
            device_manager = ids_peak.DeviceManager.Instance()

            # Update the device manager
            device_manager.Update()

            # Return if no device was found
            if device_manager.Devices().empty():
                #print("No device found. Exiting Program.")

                return False

            # Open the first openable device in the managers device list
            for device in device_manager.Devices():
                if device.IsOpenable():
                    self.__device = device.OpenDevice(ids_peak.DeviceAccessType_Control)
                    break

            # Return if no device could be opened
            if self.__device is None:
                #print("Device could not be opened!")

                return False

            # Open standard data stream
            datastreams = self.__device.DataStreams()
            if datastreams.empty():
                print("Device has no DataStream!")

                self.__device = None
                return False

            self.__datastream = datastreams[0].OpenDataStream()

            # Get nodemap of the remote device for all accesses to the genicam nodemap tree
            self.__nodemap_remote_device = self.__device.RemoteDevice().NodeMaps()[0]

            # # To prepare for untriggered continuous image acquisition, load the default user set if available and
            # # wait until execution is finished
            # try:
            #     self.__nodemap_remote_device.FindNode("UserSetSelector").SetCurrentEntry("Default")
            #     self.__nodemap_remote_device.FindNode("UserSetLoad").Execute()
            #     self.__nodemap_remote_device.FindNode("UserSetLoad").WaitUntilDone()
            # except ids_peak.Exception:
            #     # Userset is not available
            #     pass

            # To prepare for scanning objects, load the correct configuration file
            # print('Starte das Einlesen.')

            # try:
            #     # file contains the fully qualified path to the file
            #     file = "./config_camera.cset"
                
            #     # Load from file
            #     self.__nodemap_remote_device.LoadFromFile(file)

            #     print('Mitten im Einlesen.')

            #     print('Camera parameters set.')

            # except Exception as e:
            #     # print(e)

            #     print('Es gab einen Fehler beim Einlesen. ')
            #     print(e)

            # print('Einlesen sollte abgeschlossen sein.')

            # Get the payload size for correct buffer allocation
            payload_size = self.__nodemap_remote_device.FindNode("PayloadSize").Value()

            # Get minimum number of buffers that must be announced
            buffer_count_max = self.__datastream.NumBuffersAnnouncedMinRequired()

            # Allocate and announce image buffers and queue them
            for i in range(buffer_count_max):
                buffer = self.__datastream.AllocAndAnnounceBuffer(payload_size)
                self.__datastream.QueueBuffer(buffer)

            return True
        except ids_peak.Exception as e:
            print(self, "Exception", str(e))

        return False

    def __close_device(self):
        """
        Stop acquisition if still running and close datastream and nodemap of the device
        """

        # Stop Acquisition in case it is still running
        self.__stop_acquisition()

        # If a datastream has been opened, try to revoke its image buffers
        if self.__datastream is not None:
            try:
                for buffer in self.__datastream.AnnouncedBuffers():
                    self.__datastream.RevokeBuffer(buffer)
            except Exception as e:
                print(self, "Exception", str(e))

    def __start_acquisition(self):
        """
        Start Acquisition on camera and start the acquisition timer to receive and display images

        :return: True/False if acquisition start was successful
        """

        # Check that a device is opened and that the acquisition is NOT running. If not, return.
        if self.__device is None:
            return False
        if self.__acquisition_running is True:
            return True

        # Get the maximum framerate possible, limit it to the configured FPS_LIMIT. If the limit can't be reached, set
        # acquisition interval to the maximum possible framerate
        try:
            max_fps = self.__nodemap_remote_device.FindNode("AcquisitionFrameRate").Maximum()
            target_fps = min(max_fps, FPS_LIMIT)
            self.__nodemap_remote_device.FindNode("AcquisitionFrameRate").SetValue(target_fps)
        except ids_peak.Exception:
            # AcquisitionFrameRate is not available. Unable to limit fps. Print warning and continue on.
            #print(self, "Warning",
                                #"Unable to limit fps, since the AcquisitionFrameRate Node is"
                                #" not supported by the connected camera. Program will continue without limit.")

            # Publish Event: Warning Unable to limit fps, since the AcquisitionFrameRate Node is
            # not supported by the connected camera. Program wil continue without limit
            print(self, "warning")


        # Setup acquisition timer accordingly
        #self.__acquisition_timer.setInterval((1 / target_fps) * 1000)
        #self.__acquisition_timer.setSingleShot(False)
        #self.__acquisition_timer.timeout.connect(self.on_acquisition_timer)

        try:
            # Lock critical features to prevent them from changing during acquisition
            self.__nodemap_remote_device.FindNode("TLParamsLocked").SetValue(1)

            # Start acquisition on camera
            self.__datastream.StartAcquisition()
            self.__nodemap_remote_device.FindNode("AcquisitionStart").Execute()
            self.__nodemap_remote_device.FindNode("AcquisitionStart").WaitUntilDone()
        except Exception as e:
            print("Exception: " + str(e))

            return False

        # Start acquisition timer
        # self.__acquisition_timer.start()
        self.__acquisition_running = True

        return True

    def __stop_acquisition(self):
        """
        Stop acquisition timer and stop acquisition on camera
        :return:
        """

        # Check that a device is opened and that the acquisition is running. If not, return.
        if self.__device is None or self.__acquisition_running is False:
            return

        # Otherwise try to stop acquisition
        try:
            remote_nodemap = self.__device.RemoteDevice().NodeMaps()[0]
            remote_nodemap.FindNode("AcquisitionStop").Execute()

            # Stop and flush datastream
            self.__datastream.KillWait()
            self.__datastream.StopAcquisition(ids_peak.AcquisitionStopMode_Default)
            self.__datastream.Flush(ids_peak.DataStreamFlushMode_DiscardAll)

            self.__acquisition_running = False

            # Unlock parameters after acquisition stop
            if self.__nodemap_remote_device is not None:
                try:
                    self.__nodemap_remote_device.FindNode("TLParamsLocked").SetValue(0)
                except Exception as e:
                    print(self, "Exception", str(e))

        except Exception as e:
            print(self, "Exception", str(e))

    def __check_and_reconnect__(self):
        while self.running:
            if not self.connected:
                # Try to reconnect
                print("Verbindung fehlgeschlagen. Versuch, neu zu verbinden.")
                self.connected = self.__try_connect__()
            time.sleep(5)

    def store_live_image(self):
        while self.running:
            if self.connected:
                try:
                    buffer = self.__datastream.WaitForFinishedBuffer(5000)
                    width = buffer.Width()
                    height = buffer.Height()
                    px = buffer.PixelFormatNamespace()

                    ipl_image = ids_peak_ipl_extension.BufferToImage(buffer)
                    converted_ipl_image = ipl_image.ConvertTo(ids_peak_ipl.PixelFormatName_BGRa8)

                    image_np_array = converted_ipl_image.get_numpy_1D()
                    image_np_array = image_np_array.reshape(height, width, 4)

                    # Save the current live image in the instance variable with lock
                    with self.live_image_condition:
                        self.live_image = image_np_array.copy()
                        self.save_small_image(self.live_image)
                        self.live_image_condition.notify_all()

                    # Verkleinern und Speichern des Bildes im Ringbuffer
                    #self.save_small_image(self.live_image)

                    self.__datastream.QueueBuffer(buffer)

                except Exception as e:
                    self.connected = False

                    self.__check_and_reconnect__()

            else:
                time.sleep(1)
    
    def get_current_frame(self, timeout=1):  # Default timeout in seconds
        # Check if connection is active to prevent that the current frame is out of date
        if not self.connected:
            raise ConnectionError("Keine Verbindung zur Kamera.")

        try:
            print("Get new Frame")
            
            # Try to get the newest image
            with self.live_image_condition:
                print(f"Aufgerufen")
                is_new_image_available = self.live_image_condition.wait_for(lambda: self.live_image is not None, timeout)
                if not is_new_image_available:
                    raise TimeoutError("Timeout beim Warten auf das neueste Kamerabild.")

                if self.live_image is None:
                    return None

                frame_copy = self.live_image.copy()

                # Ensure the frame is in BGRA format
                if frame_copy.shape[2] == 3:  # Check if the image has 3 channels (BGR)
                    frame_copy = cv2.cvtColor(frame_copy, cv2.COLOR_BGR2BGRA)

                print(f"Methode fertig")
                self.live_image_condition.notify_all()

                return frame_copy

        except Exception as e:
            print("Exception: " + str(e))

            raise
            #buffer hier
    def save_small_image(self, image):
        small_image = cv2.resize(image, (300, 300))
        with self.buffer_lock:
            self.small_images_buffer.append(small_image)

    def get_latest_small_frame(self):
        with self.buffer_lock:
            if self.small_images_buffer:
                return self.small_images_buffer[-1].copy()  # Returns a copy of the small image
            else:
                return None  # No image available
            
    def get_previous_small_frame(self):
        with self.buffer_lock:
            # Ensure, that enough images are stored
            if len(self.small_images_buffer) > 1:
                # Return the previous small frame
                return self.small_images_buffer[-2].copy()
            else:
                return None  # Not enough images
