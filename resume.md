# Session Resume (June 25, 2026)

## Čo sme dnes vyriešili
1. **Verifikácia Kamery:** Spustili sme diagnostiku na Raspberry Pi a overili, že natívna knižnica `Picamera2` bezchybne číta obraz z Camera Module 3 (IMX708). 
2. **Oprava orientácie a servomotorov kamery:** 
   - Zistili sme skutočné zapojenie (Pan = kanál 0, Tilt = kanál 1) a opravili kód v `arm.py`.
   - Pridali sme pre ne bezpečné `pulse_width` rozsahy.
   - Odstránili sme zbytočnú softvérovú rotáciu obrazu v `app.py`.
3. **Kompletný redizajn Web UI (Gamepad Mode):**
   - Prepísali sme `index.html` z obyčajných tlačidiel na plnohodnotné mobilné Gamepad rozhranie pre režim "Landscape" (na šírku).
   - Pridali sme Dark Mode a Glassmorphism dizajn.
   - Vyriešili sme usporiadanie (Ľavý palec: podvozok + uhol kamery, Pravý palec: kĺby ramena + uvoľnenie serv).
   - Tlačidlo "Uvoľniť Servá" bolo bezpečne integrované do pravého panelu tak, aby neutieklo mimo displej.

## Čo nás čaká nabudúce
*   **Sekvenčné bezpečné parkovanie:** (Priorita) Nakalibrovať funkciu `park_arm()`, aby sa kĺby ramena poskladali postupne a nedošlo k mechanickej kolízii zápästia s ramenom.
*   **Predprogramované pózy:** Namapovanie komplexných pohybov (napríklad `pose_grab()`) priamo do kódu a vytvorenie príslušných tlačidiel v novom UI.

## Rýchle príkazy
*   Spustenie na RPi: `uv run app.py`
*   Prístup cez web: `http://<IP_ADRESA>:5000`
