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
  const [collectionsByAngelId, setCollectionsByAngelId] = useState({});

  const isMobile = useMediaQuery("(max-width:600px)");

  useEffect(() => {
    const init = async () => {
      setLoading(true);

      const [{ user }, angels] = await Promise.all([
        api.auth.getUser().catch(() => ({ user: null })),
        fetchAngelsImages(),
      ]);

      const uid = user?.id || null;
      setUserId(uid);

      let countsByAngelId = {};
      if (uid) {
        try {
          const collections = await api.collections.getByUser(uid);
          setCollectionsByAngelId(
            Object.fromEntries(
              (collections || []).map((c) => [
                c.angel_id,
                {
                  angel_id: c.angel_id,
                  count: c.count ?? 0,
                  trade_count: c.trade_count ?? (c.willing_to_trade ? 1 : 0),
                  is_favorite: !!c.is_favorite,
                  in_search_of: !!c.in_search_of,
                  willing_to_trade: !!c.willing_to_trade,
                },
              ])
            )
          );

          countsByAngelId = Object.fromEntries((collections || []).map((c) => [c.angel_id, c.count ?? 0]));
        } catch (e) {
          console.error("Error fetching collections:", e);
        }
      }

      setImages(
        (angels || []).map((angel) => ({
          id: angel.id,
          name: angel.name,
          imageBwUrl: angel.image_bw_url,
          imageOpacityUrl: angel.image_opacity_url,
          imageColorUrl: angel.image_url,
          count: countsByAngelId[angel.id] ?? 0,
        }))
      );

      setLoading(false);
    };

    init();
  }, []);

  const refreshCollections = async () => {
    if (!userId) return;
    try {
      const collections = await api.collections.getByUser(userId);
      setCollectionsByAngelId(
        Object.fromEntries(
          (collections || []).map((c) => [
            c.angel_id,
            {
              angel_id: c.angel_id,
              count: c.count ?? 0,
              trade_count: c.trade_count ?? (c.willing_to_trade ? 1 : 0),
              is_favorite: !!c.is_favorite,
              in_search_of: !!c.in_search_of,
              willing_to_trade: !!c.willing_to_trade,
            },
          ])
        )
      );
    } catch (e) {
      console.error("Error refreshing collections:", e);
    }
  };

  const upsertCollection = async (angelId, next) => {
    if (!userId) return;

    const payload = {
      angel_id: angelId,
      count: next.count ?? 0,
      trade_count: next.trade_count ?? 0,
      is_favorite: !!next.is_favorite,
      in_search_of: !!next.in_search_of,
      willing_to_trade: !!next.willing_to_trade,
    };

    // If nothing is set and count is 0, delete the row
    const shouldDelete =
      (payload.count ?? 0) === 0 &&
      (payload.trade_count ?? 0) === 0 &&
      !payload.is_favorite &&
      !payload.in_search_of &&
      !payload.willing_to_trade;

    try {
      if (shouldDelete) {
        await api.collections.delete(userId, angelId);
      } else {
        await api.collections.upsert(userId, payload);
      }
    } catch (e) {
      console.error("Error updating collection:", e);
    } finally {
      await refreshCollections();
    }
  };

  const handleBookmarkAdd = async (type, angelId) => {
    if (!userId) return;

    const current = collectionsByAngelId[angelId] || {
      angel_id: angelId,
      count: 0,
      is_favorite: false,
      in_search_of: false,
      willing_to_trade: false,
    };

    let next = { ...current };

    switch (type) {
      case "FAV":
        // FAV can be owned or not; it does not change count
        next.is_favorite = !current.is_favorite;
        break;
      case "ISO":
        // ISO means user does NOT own it
        if (current.in_search_of) {
          next.in_search_of = false;
        } else {
          next.in_search_of = true;
          next.count = 0;
          next.trade_count = 0;
          next.willing_to_trade = false;
        }
        break;
      case "WTT":
        // WTT means user DOES own it
        if ((current.count ?? 0) <= 0) {
          console.warn("Set count > 0 before marking WTT.");
          return;
        }
        if (current.willing_to_trade) {
          next.willing_to_trade = false;
          next.trade_count = 0;
        } else {
          next.willing_to_trade = true;
          next.trade_count = 1; // trade ONE by default (not full owned count)
        }
        break;
      default:
        return;
    }

    await upsertCollection(angelId, next);
  };

  const handleCountChange = async (angelId, newCount) => {
    if (!userId) return;

    const current = collectionsByAngelId[angelId] || {
      angel_id: angelId,
      count: 0,
      is_favorite: false,
      in_search_of: false,
      willing_to_trade: false,
    };

    let next = { ...current, count: newCount };

    // If user now owns it, ISO must be removed.
    if ((newCount ?? 0) > 0) {
      next.in_search_of = false;
    }

    // If user no longer owns it, cannot be WTT.
    if ((newCount ?? 0) === 0) {
      next.willing_to_trade = false;
      next.trade_count = 0;
    }

    // Clamp trade_count to owned count
    if ((next.trade_count ?? 0) > (next.count ?? 0)) {
      next.trade_count = next.count ?? 0;
      if ((next.trade_count ?? 0) === 0) {
        next.willing_to_trade = false;
      }
    }

    await upsertCollection(angelId, next);
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
              {(() => {
                const c = collectionsByAngelId[angel.id];
                const count = c?.count ?? 0;
                return (
              <SonnyAngelCard
                id={angel.id}
                name={angel.name}
                imageBwUrl={angel.imageBwUrl}
                imageOpacityUrl={angel.imageOpacityUrl}
                imageColorUrl={angel.imageColorUrl}
                count={count}
                isFavorite={c?.is_favorite}
                inSearchOf={c?.in_search_of}
                willingToTrade={c?.willing_to_trade}
                onCountChange={(newCount) => handleCountChange(angel.id, newCount)}
                onBookmarkAdd={(type) => handleBookmarkAdd(type, angel.id)}
              />
                );
              })()}
            </Grid>
          ))
        )}
      </Grid>
    </Box>
  );
}

