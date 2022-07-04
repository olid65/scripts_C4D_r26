"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam
Description:
    - Adds all Cinema 4D files from a selected folder to the render queue.
Class/method highlighted:
    - c4d.documents.BatchRender
    - c4d.documents.GetBatchRender()
    - BatchRender.AddFile()
"""
import c4d
import os


def main():
    fn = os.path.join(doc.GetDocumentPath(),doc.GetDocumentName())
    # Retrieves the batch render instance
    br = c4d.documents.GetBatchRender()
    if br is None:
        raise RuntimeError("Failed to retrieve the batch render instance.")
    
    
    br.AddFile(fn, br.GetElementCount())
    if not br.IsRendering():
        br.SetRendering(c4d.BR_START)

    # Opens the Batch Render
    br.Open()


if __name__ == "__main__":
    main()