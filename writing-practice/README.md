# Writing practice

[Demo video](https://www.loom.com/share/33409d0227c84a9d8cc6ad96cd1faa5c?sid=877d82f9-77d7-4e07-8cc6-2df5da330a1e)

## Setup

Starts up the lang portal API and the writing practice app:
```
make start
```

## Domain knowledge gathered

- There are tools for extracting Italian text (OCR): tesseract, Amazon textract
- tesseract worked perfectly for printed characters but failed to recongize handwritten text. Additional tweaking and learning would have been necessary to make it work
- Amazon textract worked very well, but oddly enough it produced a better result when the image was not preprocessed vs. when it was.
- tesseract worked better with preprocessed images (tresholding, grayscale, etc.)
- Amazon textract had issues with accented characters and that resulted in difficulties for the LLM to grade the translation
- The LLM couldn't disregard the issues with the accents, further prompt engineering or using a smarter model may be required to achieve this
