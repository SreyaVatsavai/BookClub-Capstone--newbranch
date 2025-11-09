// src/components/layout/Footer.jsx
import React from "react";
import { Box, Typography } from "@mui/material";

export default function Footer() {
  return (
    <Box
      sx={{
        bgcolor: "rgba(0, 0, 0, 0.8)",
        color: "white",
        py: 2,
        px: 3,
        textAlign: "center",
      }}
    >
      <Typography variant="body2">
        © 2025 BookClub. All rights reserved.
      </Typography>
      <Typography variant="caption" sx={{ display: "block", mt: 1 }}>
        Discover, discuss, and share your favorite books with like-minded
        readers.
      </Typography>
    </Box>
  );
}
