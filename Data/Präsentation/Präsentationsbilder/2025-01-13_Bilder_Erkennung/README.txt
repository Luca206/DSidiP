"01-02" (Teil mit Bohrung [<- Schwerpunkt/e kann/können in Bohrung liegen!]):

 - 01-02_0: (Eingabe-)Bild
 - 01-02_1: Maske
 - 01-02_2: Maske mit eingezeichneten äußeren und inneren Konturen
 - 01-02_3: Maske mit eingezeichnetem äußeren und inneren Schwerpunkt <- Schwerpunkt(e) liegen in Bohrung: Euklidische Distanztransformation notwendig!
 - 01-02_4: Ergebnis euklidischer Distanztransformation (eDt)
            (Je weiter entfernt ein weißes Pixel von nächsten schwarzen Pixel in der Maske ist, desto heller ist es)
            (Schwarze Pixel im weißen Teil der Maske erzeugen "Löcher" in Ergebis von eDt)
            (Hellstes Pixel (am weitesten entfernt vom nächsten schwarzen Pixel) ist mit 'X' markiert) <- Punkt ('X') zum Greifen für Teil mit Bohrung

 - 01-02_5: Maske mit hellstem Pixel aus Ergebnis von eDt (01-02_4) mit 'X' markiert.
            (Kreis dient zum Verständnis:
             Hellstes Pixel ist Mittelpunkt des größten Kreises,
             welches in den weißen Teil der Maske gelegt werden kann, ohne schwarze Pixel zu berühren.
             Der Wert (Helligkeit) des Pixels ist der Radius dieses Kreises.
             [Anbei: Wert des Pixels interessiert uns nicht, nur die Koordinaten!])

"01-06" (Teil ohne Bohrung):

 - 01-06_0: (Eingabe-)Bild
 - 01-06_1: Maske
 - 01-06_2: Maske mit eingezeichneten äußeren Konturen
 - 01-06_3: Maske mit eingezeichnetem äußeren Schwerpunkt <- Punkt ('X') zum Greifen für Teil ohne Bohrung