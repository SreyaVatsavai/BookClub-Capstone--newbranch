// src/components/FloatingImages.jsx
import React from "react";
import { Box } from "@mui/material";

export default function FloatingImages() {
  // Create an array of image sources
  const imageSources = Array.from(
    { length: 13 },
    (_, i) => `/pic${i + 1}.jpeg`
  );

  return (
    <>
      <Box
        sx={{
          position: "relative",
          height: "280px", // Increased height
          mt: 4,
          overflow: "hidden",
          width: "100%",
          "&:hover": {
            animationPlayState: "paused",
          },
        }}
      >
        <Box
          sx={{
            display: "flex",
            animation: "scroll 30s linear infinite",
            width: "max-content",
          }}
        >
          {imageSources.map((src, index) => (
            <Box
              key={index}
              component="img"
              src={src}
              alt={`Book ${index + 1}`}
              sx={{
                height: "260px",
                width: "180px",
                objectFit: "contain",
                borderRadius: "8px",
                mx: 2,
                boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
              }}
              onError={(e) => {
                e.target.style.display = "none";
              }}
            />
          ))}
          {/* Duplicate images for seamless looping */}
          {imageSources.map((src, index) => (
            <Box
              key={`duplicate-${index}`}
              component="img"
              src={src}
              alt={`Book ${index + 1} duplicate`}
              sx={{
                height: "260px",
                width: "180px",
                objectFit: "contain",
                borderRadius: "8px",
                mx: 2,
                boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
              }}
              onError={(e) => {
                e.target.style.display = "none";
              }}
            />
          ))}
        </Box>
      </Box>

      {/* CSS for the animation */}
      <style jsx>{`
        @keyframes scroll {
          0% {
            transform: translateX(0);
          }
          100% {
            transform: translateX(-50%);
          }
        }
      `}</style>
    </>
  );
}
