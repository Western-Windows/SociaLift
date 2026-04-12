// src/components/VideoModal.tsx
import { useEffect } from "react";

interface VideoModalProps {
  isOpen: boolean;
  onClose: () => void;
  videoUrl: string;
}

export const VideoModal = ({ isOpen, onClose, videoUrl }: VideoModalProps) => {
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    if (isOpen) {
      document.addEventListener("keydown", handleEscape);
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.removeEventListener("keydown", handleEscape);
      document.body.style.overflow = "";
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm transition-all duration-300"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label="Video player"
    >
      <div
        className="relative w-[90vw] max-w-4xl aspect-video rounded-xl overflow-hidden shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <iframe
          src={`${videoUrl}?autoplay=1`}
          title="Video player"
          className="w-full h-full"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        />
        <button
          onClick={onClose}
          className="absolute -top-10 right-0 text-white text-2xl hover:scale-110 transition-transform duration-200 focus:outline-none focus:ring-2 focus:ring-white rounded-full"
          aria-label="Close video"
        >
          ✕
        </button>
      </div>
    </div>
  );
};
