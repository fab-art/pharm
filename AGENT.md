# Tech Stack and Coding Standards
- **Framework:** Django 5.x structured with clean encapsulation layers (Utilities, Models, Views, Templates).
- **Frontend Architecture:** Modern, reactive Tailwind CSS (v3+ via CDN for rapid loading), custom layout, and Vanilla ES6+ Javascript components. No heavy SPA frameworks.
- **Interactive Visualizations:** High-performance data mapping using Vis.js via standard HTML injection layers.
- **Database Engine:** SQLite for initial local development; ready to leverage environment configurations for external relational systems.
- **Asynchronous Processing Policy:** Heavy memory calculations, report generations, and image generation MUST use Python `io.BytesIO` in-memory buffers. File drops to the local ephemeral disk are strictly prohibited.
- **Python Code Layout:** Adhere strictly to PEP 8. Maintain clear exception logging inside utilities and capture traceback errors to user-facing template warnings.