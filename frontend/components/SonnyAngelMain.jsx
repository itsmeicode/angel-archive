import React, { useState, useEffect, useMemo } from "react";
import { Box, Grid, Typography, useMediaQuery } from "@mui/material";
import { SonnyAngelCard } from "./SonnyAngelCard";
import { SearchBar } from "./SearchBar";
import { Filter } from "./Filter";
import { fetchAngelsImages } from "../src/utils/queries";
import api from "../src/services/api";

export function SonnyAngelMain({ toggleLeftBar }) {
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [userId, setUserId] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [collectionsByAngelId, setCollectionsByAngelId] = useState({});
  const [filters, setFilters] = useState({
    owned: "all",
    seriesIds: [],
    fav: false,
    iso: false,
    wtt: false,
    sortBy: "name-asc",
  });

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
          series_id: angel.series_id,
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
        // FAV only for owned angels (count > 0)
        if ((current.count ?? 0) <= 0 && !current.is_favorite) return;
        next.is_favorite = !current.is_favorite;
        break;
      case "ISO":
        // Toggle ISO; keep current count so owned angels stay colored with count (e.g. want 2, have 1)
        if (current.in_search_of) {
          next.in_search_of = false;
        } else {
          next.in_search_of = true;
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

    // ISO is not auto-removed when adding count — user may want 2+ and will clear ISO manually when done.

    // If user no longer owns it, remove WTT and FAV.
    if ((newCount ?? 0) === 0) {
      next.willing_to_trade = false;
      next.trade_count = 0;
      next.is_favorite = false;
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

  const filteredImages = useMemo(() => {
    const filtered = images.filter((angel) => {
      const nameMatch = angel.name.toLowerCase().includes(searchTerm.toLowerCase());
      if (!nameMatch) return false;

      const c = collectionsByAngelId[angel.id] || {
        count: 0,
        is_favorite: false,
        in_search_of: false,
        willing_to_trade: false,
      };

      // Ownership filter
      if (filters?.owned === "owned" && (c.count ?? 0) <= 0) return false;
      if (filters?.owned === "unowned" && (c.count ?? 0) > 0) return false;

      // Series filter
      if (filters?.seriesIds && filters.seriesIds.length > 0) {
        if (!filters.seriesIds.includes(angel.series_id)) return false;
      }

      // Status filters (OR semantics: if multiple selected, show items matching any)
      const statusFilters = [];
      if (filters?.fav) statusFilters.push(c.is_favorite);
      if (filters?.iso) statusFilters.push(c.in_search_of);
      if (filters?.wtt) statusFilters.push(c.willing_to_trade);
      
      // If any status filters are active, item must match at least one
      if (statusFilters.length > 0 && !statusFilters.some(Boolean)) return false;

      return true;
    });

    // Apply sorting
    const sortBy = filters?.sortBy || "name-asc";
    const sorted = [...filtered].sort((a, b) => {
      const cA = collectionsByAngelId[a.id] || { count: 0 };
      const cB = collectionsByAngelId[b.id] || { count: 0 };
      const countA = cA.count ?? 0;
      const countB = cB.count ?? 0;

      switch (sortBy) {
        case "name-asc":
          return a.name.localeCompare(b.name);
        case "name-desc":
          return b.name.localeCompare(a.name);
        case "count-desc":
          return countB - countA;
        case "count-asc":
          return countA - countB;
        default:
          return 0;
      }
    });

    return sorted;
  }, [images, searchTerm, collectionsByAngelId, filters]);

  return (
    <Box
      flex={4}
      p={2}
      onClick={() => isMobile && toggleLeftBar()}
      sx={{ cursor: isMobile ? "pointer" : "default" }}
    >
      <Typography variant="h4" gutterBottom>
        Full Collection
      </Typography>

      <Box
        sx={{
          display: "flex",
          flexDirection: { xs: "column", md: "row" },
          gap: 3,
          mt: 1,
        }}
      >
        <Box
          sx={{
            width: { xs: "100%", md: 320 },
            flexShrink: 0,
            bgcolor: "rgba(255,255,255,0.9)",
            borderRadius: 2,
            boxShadow: 2,
            p: 2,
            height: "fit-content",
            alignSelf: "flex-start",
            position: { md: "sticky" },
            top: { md: "20px" },
            maxHeight: { md: "calc(100vh - 40px)" },
            overflowY: { md: "auto" },
          }}
        >
          <SearchBar
            options={images.map((angel) => angel.name)}
            onSearch={setSearchTerm}
          />
          <Box mt={2}>
            <Filter onFilterChange={setFilters} />
          </Box>
        </Box>

        <Box sx={{ flexGrow: 1 }}>
          <Box
            sx={{
              display: "grid",
              gridTemplateColumns: {
                xs: "1fr",
                sm: "repeat(2, 1fr)",
                md: "repeat(3, 1fr)",
                lg: "repeat(5, 1fr)",
              },
              gap: 2,
            }}
          >
            {loading ? (
              <Typography variant="body1">Loading images...</Typography>
            ) : (
              filteredImages.map((angel) => {
                const c = collectionsByAngelId[angel.id];
                const count = c?.count ?? 0;
                return (
                  <SonnyAngelCard
                    key={angel.id}
                    id={angel.id}
                    name={angel.name}
                    imageBwUrl={angel.imageBwUrl}
                    imageOpacityUrl={angel.imageOpacityUrl}
                    imageColorUrl={angel.imageColorUrl}
                    count={count}
                    isFavorite={c?.is_favorite}
                    inSearchOf={c?.in_search_of}
                    willingToTrade={c?.willing_to_trade}
                    onCountChange={(newCount) =>
                      handleCountChange(angel.id, newCount)
                    }
                    onBookmarkAdd={(type) =>
                      handleBookmarkAdd(type, angel.id)
                    }
                  />
                );
              })
            )}
          </Box>
        </Box>
      </Box>
    </Box>
  );
}

