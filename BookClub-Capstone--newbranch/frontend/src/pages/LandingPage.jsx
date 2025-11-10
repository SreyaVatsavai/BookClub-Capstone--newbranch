// src/pages/LandingPage.jsx
import React from "react";
import { Box, Typography, Button, Container, Paper } from "@mui/material";
import { useNavigate } from "react-router-dom";
import MenuBookIcon from "@mui/icons-material/MenuBook";
import FloatingImages from "./FloatingImages";

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <Box
      sx={{
        minHeight: "100vh",
        background: `linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.7)), 
                     url('https://images.unsplash.com/photo-1507842217343-583bb7270b66?q=80&w=1920')`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundAttachment: "fixed",
        display: "flex",
        flexDirection: "column",
        position: "relative",
      }}
    >
      {/* Top Right Auth Buttons */}

      {/* Main Content */}
      <Container
        maxWidth="md"
        sx={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          textAlign: "center",
          py: 8,
        }}
      >
        {/* Logo/Icon */}
        <Paper
          elevation={0}
          sx={{
            backgroundColor: "rgba(255, 215, 0, 0.15)",
            borderRadius: "50%",
            p: 3,
            mb: 4,
            backdropFilter: "blur(10px)",
          }}
        >
          <MenuBookIcon
            sx={{
              fontSize: 80,
              color: "#ffd700",
            }}
          />
        </Paper>

        {/* Website Name */}
        <Typography
          variant="h1"
          sx={{
            color: "white",
            fontWeight: "bold",
            fontSize: { xs: "3rem", sm: "4rem", md: "5rem" },
            mb: 2,
            textShadow: "2px 2px 8px rgba(0,0,0,0.8)",
            letterSpacing: "2px",
          }}
        >
          BookClub
        </Typography>

        {/* Tagline */}
        <Typography
          variant="h5"
          sx={{
            color: "#ffd700",
            fontWeight: 500,
            fontSize: { xs: "1.2rem", sm: "1.5rem", md: "1.8rem" },
            mb: 1,
            textShadow: "1px 1px 4px rgba(0,0,0,0.8)",
            fontStyle: "italic",
          }}
        >
          Read Together, Grow Together
        </Typography>

        <Typography
          variant="h6"
          sx={{
            color: "rgba(255, 255, 255, 0.9)",
            fontWeight: 300,
            fontSize: { xs: "1rem", sm: "1.2rem" },
            mb: 6,
            maxWidth: "600px",
            textShadow: "1px 1px 4px rgba(0,0,0,0.8)",
          }}
        >
          Join reading groups, track your progress, and connect with fellow book
          lovers
        </Typography>

        {/* Call to Action */}
        <Box
          sx={{
            display: "flex",
            gap: 3,
            flexWrap: "wrap",
            justifyContent: "center",
          }}
        >
          <Button
            variant="contained"
            size="large"
            onClick={() => navigate("/register")}
            sx={{
              backgroundColor: "#ffd700",
              color: "#000",
              "&:hover": {
                backgroundColor: "#ffed4e",
                transform: "scale(1.05)",
              },
              fontWeight: "bold",
              px: 5,
              py: 1.5,
              fontSize: "1.1rem",
              transition: "all 0.3s ease",
            }}
          >
            Get Started
          </Button>
          <Button
            variant="outlined"
            size="large"
            onClick={() => navigate("/login")}
            sx={{
              color: "white",
              borderColor: "white",
              borderWidth: 2,
              "&:hover": {
                borderColor: "white",
                borderWidth: 2,
                backgroundColor: "rgba(255, 255, 255, 0.1)",
                transform: "scale(1.05)",
              },
              fontWeight: "bold",
              px: 5,
              py: 1.5,
              fontSize: "1.1rem",
              transition: "all 0.3s ease",
            }}
          >
            Sign In
          </Button>
        </Box>

        {/* Features */}
        <Box
          sx={{
            mt: 8,
            display: "flex",
            gap: 4,
            flexWrap: "wrap",
            justifyContent: "center",
            maxWidth: "800px",
          }}
        >
          <Paper
            elevation={3}
            sx={{
              backgroundColor: "rgba(255, 255, 255, 0.1)",
              backdropFilter: "blur(10px)",
              p: 3,
              minWidth: "200px",
              flex: 1,
              textAlign: "center",
              border: "1px solid rgba(255, 255, 255, 0.2)",
            }}
          >
            <Typography variant="h4" sx={{ color: "#ffd700", mb: 1 }}>
              📚
            </Typography>
            <Typography
              variant="h6"
              sx={{ color: "white", fontWeight: "bold", mb: 1 }}
            >
              Reading Groups
            </Typography>
            <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.8)" }}>
              Join or create groups with shared reading schedules
            </Typography>
          </Paper>

          <Paper
            elevation={3}
            sx={{
              backgroundColor: "rgba(255, 255, 255, 0.1)",
              backdropFilter: "blur(10px)",
              p: 3,
              minWidth: "200px",
              flex: 1,
              textAlign: "center",
              border: "1px solid rgba(255, 255, 255, 0.2)",
            }}
          >
            <Typography variant="h4" sx={{ color: "#ffd700", mb: 1 }}>
              📊
            </Typography>
            <Typography
              variant="h6"
              sx={{ color: "white", fontWeight: "bold", mb: 1 }}
            >
              Track Progress
            </Typography>
            <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.8)" }}>
              Monitor your reading with smart reminders
            </Typography>
          </Paper>

          <Paper
            elevation={3}
            sx={{
              backgroundColor: "rgba(255, 255, 255, 0.1)",
              backdropFilter: "blur(10px)",
              p: 3,
              minWidth: "200px",
              flex: 1,
              textAlign: "center",
              border: "1px solid rgba(255, 255, 255, 0.2)",
            }}
          >
            <Typography variant="h4" sx={{ color: "#ffd700", mb: 1 }}>
              💬
            </Typography>
            <Typography
              variant="h6"
              sx={{ color: "white", fontWeight: "bold", mb: 1 }}
            >
              Discuss
            </Typography>
            <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.8)" }}>
              Share thoughts and insights with your group
            </Typography>
          </Paper>
        </Box>
      </Container>

      {/* Footer */}
      <Box
        sx={{
          textAlign: "center",
          py: 3,
          color: "rgba(255, 255, 255, 0.6)",
        }}
      >
        <FloatingImages />
        <Typography variant="body2">
          © 2025 BookClub. All rights reserved.
        </Typography>
      </Box>
    </Box>
  );
}
