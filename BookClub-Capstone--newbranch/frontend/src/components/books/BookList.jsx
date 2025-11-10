// src/components/books/BookList.js
import React, { useState, useEffect } from "react";
import {
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Box,
  Typography,
} from "@mui/material";
import api from "../../api/axiosConfig";
import BookCard from "./BookCard"; // We'll keep BookCard as a sub-component
import { useNavigate } from "react-router-dom";

export default function BookList({ onBookSelect }) {
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [genre, setGenre] = useState("");
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [genres] = useState([
    "Fiction",
    "Non-Fiction",
    "Sci-Fi",
    "Mystery",
    "Biography",
    "Fantasy",
    "History",
  ]);

  const handleSearch = async () => {
    setLoading(true);
    try {
      const params = {};
      if (search) params.search = search;
      if (genre) params.genre = genre;
      const res = await api.get("/books/", { params });
      setBooks(res.data);
    } catch (err) {
      console.error("Failed to fetch books", err);
      setBooks([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleSearch(); // Load all books on mount
  }, []);

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h5" gutterBottom>
        Find a Book
      </Typography>

      {/* Search & Filter */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Search by title or author"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            size="small"
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <FormControl fullWidth size="small">
            <InputLabel>Genre</InputLabel>
            <Select
              value={genre}
              label="Genre"
              onChange={(e) => setGenre(e.target.value)}
            >
              <MenuItem value="">All Genres</MenuItem>
              {genres.map((g) => (
                <MenuItem key={g} value={g}>
                  {g}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={2}>
          <Box sx={{ height: "100%", display: "flex", alignItems: "flex-end" }}>
            <Box
              component="button"
              onClick={handleSearch}
              sx={{
                width: "100%",
                py: 1,
                px: 2,
                borderRadius: 1,
                border: "1px solid",
                borderColor: "primary.main",
                backgroundColor: "primary.main",
                color: "white",
                cursor: "pointer",
                "&:hover": { backgroundColor: "primary.dark" },
              }}
            >
              Search
            </Box>
          </Box>
        </Grid>
      </Grid>

      {/* Book List */}
      {loading ? (
        <Typography>Loading books...</Typography>
      ) : books.length === 0 ? (
        <Typography>No books found.</Typography>
      ) : (
        <Grid container spacing={3}>
          {books.map((book) => (
            <Grid item xs={12} sm={6} md={4} key={book.id}>
              <BookCard
                book={book}
                onSelect={() => {
                  // If a parent passed an onBookSelect prop, call it
                  if (onBookSelect) return onBookSelect(book);
                  // Otherwise navigate to the book detail page
                  return navigate(`/books/${book.id}`);
                }}
              />
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
}
