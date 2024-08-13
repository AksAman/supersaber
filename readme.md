### Configs

```python
PIXEL_PIN = board.D0
BUTTON_PIN = board.D1
SHORT_PRESS_DURATION = 500
LONG_PRESS_DURATION = 2000
BRIGHTNESS = 0.3
TOTAL_PIXELS = 87
```

### Running the audio server

1. Setup your virtual environment
2. Install the requirements
   ```
   pip install -r requirements.txt
   ```
3. Run the server
   ```
   uvicorn  sabersocket.app.main:app --reload --port 8002 --host 0.0.0.0
   ```
4. Endpoints:
   ```
   GET /audio-values
   WS /audio
   ```

### Syncing the code with the ESP32

1.  open `./scripts/config.sh` and update the variables marked under `# Update these variables`.
2.  Be sure to install nodemon:

    ```bash
    npm install -g nodemon
    ```

    or, if you're using `bun`:

    ```
    bun add -g nodemon
    ```

3.  Run
    ```
    ./scripts/run.sh
    ```
