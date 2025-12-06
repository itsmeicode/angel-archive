import React, { useState, useEffect } from "react";
import { Box, Grid, Typography, useMediaQuery } from "@mui/material";
import { SonnyAngelCard } from "./SonnyAngelCard";
import { SearchBar } from "./SearchBar";
import { fetchAngelsImages } from "../src/utils/queries";
import api from "../src/services/api";

export function SonnyAngelMain({ toggleLeftBar }) {
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [userId, setUserId] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");

  const isMobile = useMediaQuery("(max-width:600px)");

  useEffect(() => {
    const loadImages = async () => {
      const angels = await fetchAngelsImages();
      if (angels.length) {
        setImages(
          angels.map((angel) => ({
            id: angel.id,
            name: angel.name,
            imageUrl: angel.image_bw_url,
          }))
        );
      }
      setLoading(false);
    };

    const getUser = async () => {
      const { user } = await api.auth.getUser();
      if (user) {
        setUserId(user.id);
      }
    };

    loadImages();
    getUser();
  }, []);

  const handleBookmarkAdd = async (type, angelId, angelName) => {
    if (!userId) return;

    let updateFields = {};

    switch (type) {
      case "FAV":
        updateFields.is_favorite = true;
        break;
      case "ISO":
        updateFields.in_search_of = true;
        break;
      case "WTT":
        updateFields.willing_to_trade = true;
        break;
      default:
        return;
    }

    try {
      await api.collections.upsert(userId, { angel_id: angelId, ...updateFields });
      console.log("Bookmark updated successfully");
    } catch (error) {
      console.error("Error updating bookmark:", error);
    }
  };

  const filteredImages = images.filter((angel) =>
    angel.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Box
      flex={4}
      p={2}
      onClick={() => isMobile && toggleLeftBar()} 
      sx={{ cursor: isMobile ? "pointer" : "default",}}
    >
      <Typography variant="h4" gutterBottom>
        Full Collection
      </Typography>
      <SearchBar options={images.map((angel) => angel.name)} onSearch={setSearchTerm} />
      <Grid container spacing={3} justifyContent="flex-start">
        {loading ? (
          <Typography variant="body1">Loading images...</Typography>
        ) : (
          filteredImages.map((angel) => (
            <Grid item key={angel.id} xs={6} sm={4} md={3} lg={2}>
              <SonnyAngelCard
                id={angel.id}
                name={angel.name}
                imageUrl={angel.imageUrl}
                userId={userId}
                onBookmarkAdd={handleBookmarkAdd}
                initialCount={angel.angel_count}
              />
            </Grid>
          ))
        )}
      </Grid>
    </Box>
  );
}

