# Vote app (static, GitHub Pages)

vote-app/
├── index.html
├── data/
│   ├── characters.json     <- source of truth for characters
│   └── backgrounds.json    <- source of truth for backgrounds
└── assets/
    ├── characters/         <- portrait images (any filename)
    └── backgrounds/        <- background images (any filename)

characters.json: { "characters": [ { "id": "c001", "name": "...", "portrait": "assets/characters/any-name.jpg" } ] }
backgrounds.json: { "backgrounds": [ { "id": "bg01", "image": "assets/backgrounds/any-name.jpg" } ] }

- Add/remove entries freely; the site reads the JSON on every load (min 2 characters, rounds show up to 5).
- Keep each id unique and never reuse it; votes are recorded by id.
- Portraits: square, ~400x400, <60 KB. Backgrounds: ~1920x1080 JPG/WebP, <300 KB.
- Preview locally with `python3 -m http.server` (opening index.html directly can't read the JSON).



### 🚀 Running a Local Web Server on Windows 11
1. Open your project folder in File Explorer.
2. Click the address bar, type `cmd`, and press **Enter** (this opens the command prompt right in your folder).
3. Type the command and press **Enter**: py -m http.server
4. Open your browser** and go to http://localhost:8000

### 🛑 Stopping the Server
Simply close the command prompt window (click the `X`), or press `Ctrl + C` inside the terminal.

Remember: We do this because browsers block `file:///` URLs from fetching local assets, and the server gives your app a proper `http://localhost` environment!)
