/**
 * ImageUpload component — allows users to select and upload an image for an article.
 */
import React, { useRef, useState } from "react";
import { uploadArticleImage } from "../api/articles";

/** Props for the ImageUpload component. */
interface ImageUploadProps {
  /** The ID of the article the image belongs to. */
  articleId: number;
  /** Callback invoked after a successful image upload. */
  onUploadSuccess: () => void;
}

/**
 * A file input component that uploads an image to the backend via multipart/form-data.
 * Shows an error message if the upload fails.
 *
 * @param props - Component props.
 * @returns The ImageUpload component.
 */
const ImageUpload: React.FC<ImageUploadProps> = ({ articleId, onUploadSuccess }) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  /**
   * Handles file selection from the input element.
   * @param event - The change event from the file input.
   */
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    const selected = event.target.files?.[0] ?? null;
    setFile(selected);
  };

  /**
   * Uploads the selected file to the backend.
   * Calls onUploadSuccess on completion, or sets an error message on failure.
   */
  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      await uploadArticleImage(articleId, file);
      setFile(null);
      // Reset the file input element
      if (inputRef.current) {
        inputRef.current.value = "";
      }
      onUploadSuccess();
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Failed to upload image. Please try again.";
      setError(message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div role="group" aria-label="Image upload">
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        aria-label="Select image file"
        onChange={handleFileChange}
        disabled={uploading}
      />
      <button
        type="button"
        onClick={handleUpload}
        disabled={!file || uploading}
        aria-busy={uploading}
        aria-disabled={!file || uploading}
      >
        {uploading ? "Uploading…" : "Upload"}
      </button>
      {error && (
        <p role="alert" style={{ color: "red", marginTop: "0.5rem" }}>
          {error}
        </p>
      )}
    </div>
  );
};

export default ImageUpload;
