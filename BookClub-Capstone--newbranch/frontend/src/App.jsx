// src/App.jsx
import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider, createTheme, CssBaseline } from "@mui/material";
import { AuthProvider } from "./context/AuthContext";
import ErrorBoundary from "./utils/ErrorBoundary";
import PrivateRoute from "./utils/PrivateRoute";
import LandingPage from "./pages/LandingPage.jsx";
import Home from "./pages/Home.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import BookSearch from "./pages/BookSearch.jsx";
import BookDetailPage from "./pages/BookDetailPage.jsx";
import DiscussionForum from "./pages/DiscussionForum.jsx";
import GroupPage from "./pages/GroupPage.jsx";
import ReadingPage from "./pages/ReadingPage.jsx";
import ChapterSchedulePage from "./pages/ChapterSchedulePage.jsx";

// ✅ Define the theme
const theme = createTheme({
  // You can customize the theme here later (palette, typography, etc.)
  // For now, just use the default MUI theme
});

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <AuthProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route
                path="/home"
                element={
                  <PrivateRoute>
                    <Home />
                  </PrivateRoute>
                }
              />
              <Route
                path="/books"
                element={
                  <PrivateRoute>
                    <BookSearch />
                  </PrivateRoute>
                }
              />
              <Route
                path="/books/:id"
                element={
                  <PrivateRoute>
                    <BookDetailPage />
                  </PrivateRoute>
                }
              />
              <Route
                path="/groups/:groupId"
                element={
                  <PrivateRoute>
                    <GroupPage />
                  </PrivateRoute>
                }
              />
              <Route
                path="/groups/:groupId/discussion"
                element={
                  <PrivateRoute>
                    <DiscussionForum />
                  </PrivateRoute>
                }
              />
              <Route
                path="/groups/:groupId/read"
                element={
                  <PrivateRoute>
                    <ReadingPage />
                  </PrivateRoute>
                }
              />
              <Route
                path="/groups/:groupId/schedule"
                element={
                  <PrivateRoute>
                    <ChapterSchedulePage />
                  </PrivateRoute>
                }
              />
            </Routes>
          </BrowserRouter>
        </AuthProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
