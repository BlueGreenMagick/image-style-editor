# Image Style Editor

This is an addon for editing image width and height. 

## How to use

Right click on an image in editor, click on 'Image Styles'.

Accepted formats are: `300`, `240px`, `20em`, `60%`, `auto`,`--somestring`, empty, [etc](https://developer.mozilla.org/en-US/docs/Web/CSS/height). Plain numbers(eg. `300`) are automatically converted to `300px`. Values starting with `--` (eg. `--name`) are automatically converted to `var(--name)`. Trailing and leading spaces are removed. 

You can set either only the width or the height, leave the other blank, and the image should retain its aspect ratio. If it doesn't, try going into config, and change `empty_means` to `auto`.

## Differences from ImageResizer

* Uses css height and width properties to resize images, so there is no loss of quality.
* You can modify width and height individually for each image
* Can't automatically resize images on paste.

## Credits

Credits to searene, developer of the addon [ImageResizer](https://github.com/searene/Anki-Addons/tree/master/ImageResizer)'. Some of the code for gui were reused in this addon. 
Also to glutanimate(Aristotelis P.) and others who made the addon [Image Occlusion Enhanced](https://github.com/glutanimate/image-occlusion-enhanced), which was how I figured this addon would be possible to make.
