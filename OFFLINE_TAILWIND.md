This project previously used the Tailwind CDN. To build Tailwind locally and serve it from static files (works offline):

- Install Node dependencies (once):

  npm ci

- Build the production Tailwind CSS file:

  npm run build:tailwind

This will create `static/css/tailwind.css`. The base template now links that file.

On Render (or other hosts), ensure the build step runs `npm ci` and `npm run build:tailwind` before Django `collectstatic` runs. You can add these commands to your build script or `build.sh`.
