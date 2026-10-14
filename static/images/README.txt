NovaCart homepage visual assets

hero-banner.jpg: reference lifestyle hero banner. The text and CTA in this image are part of the image, so build the actual heading and Shop Now button separately in HTML for functionality.
category-*.jpg: category tile visual references.
product-*.jpg: product image visual references. These are crops from a single concept image and may include some surrounding card styling; replace with individual licensed product photos for best production quality.

Copy these files into your Django project's static/images/ folder. Update templates with Django's {% static 'images/filename.jpg' %} paths.
