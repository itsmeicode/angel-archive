import React, { useEffect, useState, useMemo } from "react";
import { Box, Grid, Typography, useMediaQuery, Paper, Button, CircularProgress } from "@mui/material";
import { SonnyAngelCard } from "../components/SonnyAngelCard";
import { SearchBar } from "../components/SearchBar";
import { Filter } from "../components/Filter";
import api from "../src/services/api";

export const ProfilePage = () => {
    const [angels, setAngels] = useState([]);
    const [favorites, setFavorites] = useState([]);
    const [inSearchOf, setInSearchOf] = useState([]);
    const [willingToTrade, setWillingToTrade] = useState([]);
    const [username, setUsername] = useState(null);
    const [userId, setUserId] = useState(null);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState("");
    const [filters, setFilters] = useState({
        owned: "all",
        seriesIds: [],
        fav: false,
        iso: false,
        wtt: false,
        sortBy: "name-asc",
    });
    const [exportLoading, setExportLoading] = useState({ json: false, csv: false });
    const [exportStatus, setExportStatus] = useState(null);
    const [lastExport, setLastExport] = useState(null);
    const [exportError, setExportError] = useState(null);

    const isMobile = useMediaQuery("(max-width:600px)");

    const angelCategoryStyles = {
        padding: { xs: 3, sm: 4 },
        borderRadius: 4,
        backgroundColor: "rgba(255, 255, 255, 0.8)",
        textAlign: "center",
        backdropFilter: "blur(10px)",
        marginBottom: "20px",
    };

    const angelTypographyStyles = {
        color: "#111",
        textAlign: "left",
        fontWeight: "600",
        lineHeight: 1.6,
        letterSpacing: "0.5px",
        marginBottom: "16px",
        paddingBottom: "6px",
    };

    const loadCollections = async (uid) => {
        const collections = await api.collections.getByUser(uid);

        const categories = {
            favorites: [],
            inSearchOf: [],
            willingToTrade: [],
            allAngels: [],
        };

        (collections || []).forEach((collection) => {
            const angelData = {
                angels_id: collection.angels.id,
                angels_name: collection.angels.name,
                angels_series_id: collection.angels.series_id,
                angels_image_url: collection.angels.image_url,
                angels_image_bw_url: collection.angels.image_bw_url,
                angels_image_opacity_url: collection.angels.image_opacity_url,
                angel_count: collection.count ?? 0,
                trade_count: collection.trade_count ?? (collection.willing_to_trade ? 1 : 0),
                is_favorite: !!collection.is_favorite,
                in_search_of: !!collection.in_search_of,
                willing_to_trade: !!collection.willing_to_trade,
            };

            if (collection.is_favorite) categories.favorites.push(angelData);
            if (collection.in_search_of) categories.inSearchOf.push(angelData);
            if (collection.willing_to_trade) categories.willingToTrade.push(angelData);
            categories.allAngels.push(angelData);
        });

        setAngels(categories.allAngels);
        setFavorites(categories.favorites);
        setInSearchOf(categories.inSearchOf);
        setWillingToTrade(categories.willingToTrade);
    };

    useEffect(() => {
        const fetchUserAndCollections = async () => {
            const { user } = await api.auth.getUser();
            if (user) {
                setUserId(user.id);
                const userData = await api.users.getProfile(user.id);
                setUsername(userData?.username);

                await loadCollections(user.id);

                await checkExportStatus();
            }
            setLoading(false);
        };

        fetchUserAndCollections();
    }, []);

    const handleSearch = (searchTerm) => {
        setSearchTerm(searchTerm.toLowerCase());
    };

    const filterAndSortAngels = (angels) => {
        // First apply search filter
        let filtered = angels.filter((angel) =>
            angel.angels_name.toLowerCase().includes(searchTerm)
        );

        // Apply other filters
        filtered = filtered.filter((angel) => {
            // Ownership filter
            if (filters?.owned === "owned" && (angel.angel_count ?? 0) <= 0) return false;
            if (filters?.owned === "unowned" && (angel.angel_count ?? 0) > 0) return false;

            // Series filter
            if (filters?.seriesIds && filters.seriesIds.length > 0) {
                if (!filters.seriesIds.includes(angel.angels_series_id)) return false;
            }

            // Status filters (OR semantics: if multiple selected, show items matching any)
            const statusFilters = [];
            if (filters?.fav) statusFilters.push(angel.is_favorite);
            if (filters?.iso) statusFilters.push(angel.in_search_of);
            if (filters?.wtt) statusFilters.push(angel.willing_to_trade);
            
            // If any status filters are active, item must match at least one
            if (statusFilters.length > 0 && !statusFilters.some(Boolean)) return false;

            return true;
        });

        // Apply sorting
        const sortBy = filters?.sortBy || "name-asc";
        const sorted = [...filtered].sort((a, b) => {
            const countA = a.angel_count ?? 0;
            const countB = b.angel_count ?? 0;

            switch (sortBy) {
                case "name-asc":
                    return a.angels_name.localeCompare(b.angels_name);
                case "name-desc":
                    return b.angels_name.localeCompare(a.angels_name);
                case "count-desc":
                    return countB - countA;
                case "count-asc":
                    return countA - countB;
                default:
                    return 0;
            }
        });

        return sorted;
    };

    // Collect all unique angel names from all categories for search autocomplete
    const allProfileAngelNames = useMemo(() => {
        const allAngels = [...angels, ...favorites, ...inSearchOf, ...willingToTrade];
        const uniqueNames = [...new Set(allAngels.map((a) => a.angels_name))];
        return uniqueNames.sort();
    }, [angels, favorites, inSearchOf, willingToTrade]);

    const upsertOrDelete = async (angelId, next) => {
        const payload = {
            angel_id: angelId,
            count: next.count ?? 0,
            trade_count: next.trade_count ?? 0,
            is_favorite: !!next.is_favorite,
            in_search_of: !!next.in_search_of,
            willing_to_trade: !!next.willing_to_trade,
        };

        const shouldDelete =
            (payload.count ?? 0) === 0 &&
            (payload.trade_count ?? 0) === 0 &&
            !payload.is_favorite &&
            !payload.in_search_of &&
            !payload.willing_to_trade;

        if (shouldDelete) {
            await api.collections.delete(userId, angelId);
        } else {
            await api.collections.upsert(userId, payload);
        }

        await loadCollections(userId);
    };

    const handleBookmarkAdd = async (type, angelId) => {
        if (!userId) return;

        const all = [...angels, ...favorites, ...inSearchOf, ...willingToTrade];
        const current = all.find((a) => a.angels_id === angelId) || {
            angels_id: angelId,
            angel_count: 0,
            is_favorite: false,
            in_search_of: false,
            willing_to_trade: false,
        };

        const currentState = {
            count: current.angel_count ?? 0,
            trade_count: current.trade_count ?? (current.willing_to_trade ? 1 : 0),
            is_favorite: !!current.is_favorite,
            in_search_of: !!current.in_search_of,
            willing_to_trade: !!current.willing_to_trade,
        };

        let next = { ...currentState };

        switch (type) {
            case "FAV":
                // FAV only for owned angels (count > 0)
                if ((currentState.count ?? 0) <= 0 && !currentState.is_favorite) return;
                next.is_favorite = !currentState.is_favorite;
                break;
            case "ISO":
                // Toggle ISO; keep current count so owned angels stay colored with count (e.g. want 2, have 1)
                if (currentState.in_search_of) {
                    next.in_search_of = false;
                } else {
                    next.in_search_of = true;
                    next.trade_count = 0;
                    next.willing_to_trade = false;
                }
                break;
            case "WTT":
                if ((currentState.count ?? 0) <= 0) {
                    console.warn("Set count > 0 before marking WTT.");
                    return;
                }
                if (currentState.willing_to_trade) {
                    next.willing_to_trade = false;
                    next.trade_count = 0;
                } else {
                    next.willing_to_trade = true;
                    next.trade_count = 1;
                }
                break;
            default:
                return;
        }

        try {
            await upsertOrDelete(angelId, next);
        } catch (error) {
            console.error("Error updating bookmark:", error);
        }
    };

    const handleCountChange = async (angelId, newCount) => {
        if (!userId) return;

        const all = [...angels, ...favorites, ...inSearchOf, ...willingToTrade];
        const current = all.find((a) => a.angels_id === angelId) || {
            angels_id: angelId,
            angel_count: 0,
            is_favorite: false,
            in_search_of: false,
            willing_to_trade: false,
        };

        let next = {
            count: newCount,
            trade_count: current.trade_count ?? (current.willing_to_trade ? 1 : 0),
            is_favorite: !!current.is_favorite,
            in_search_of: !!current.in_search_of,
            willing_to_trade: !!current.willing_to_trade,
        };

        // ISO is not auto-removed when adding count — user may want 2+ and will clear ISO manually when done.
        if ((newCount ?? 0) === 0) {
            next.willing_to_trade = false;
            next.trade_count = 0;
            next.is_favorite = false;
        }

        if ((next.trade_count ?? 0) > (next.count ?? 0)) {
            next.trade_count = next.count ?? 0;
            if ((next.trade_count ?? 0) === 0) {
                next.willing_to_trade = false;
            }
        }

        try {
            await upsertOrDelete(angelId, next);
        } catch (error) {
            console.error("Error updating count:", error);
        }
    };

    const handleTradeCountChange = async (angelId, newTradeCount) => {
        if (!userId) return;

        const all = [...angels, ...favorites, ...inSearchOf, ...willingToTrade];
        const current = all.find((a) => a.angels_id === angelId);
        if (!current) return;

        const ownedCount = current.angel_count ?? 0;
        if (ownedCount <= 0) return;

        const clampedTrade = Math.max(0, Math.min(Number(newTradeCount) || 0, ownedCount));

        const next = {
            count: ownedCount,
            trade_count: clampedTrade,
            is_favorite: !!current.is_favorite,
            in_search_of: false, // trading implies owned
            willing_to_trade: clampedTrade > 0,
        };

        try {
            await upsertOrDelete(angelId, next);
        } catch (error) {
            console.error("Error updating trade count:", error);
        }
    };

    const checkExportStatus = async () => {
        if (!userId) return;

        try {
            const status = await api.export.getStatus(userId);
            setExportStatus(status);
            return status;
        } catch (error) {
            console.error("Error checking export status:", error);
            return null;
        }
    };

    const handleExport = async (format) => {
        if (!userId) return;

        setExportError(null);
        setExportLoading(prev => ({ ...prev, [format]: true }));

        try {
            const status = await checkExportStatus();

            if (status && !status.canExport) {
                setExportError(`Please wait ${status.timeRemaining} minutes before exporting again.`);
                setExportLoading(prev => ({ ...prev, [format]: false }));
                return;
            }

            const response = await fetch(
                `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/export/users/${userId}?format=${format}`,
                {
                    method: 'GET',
                    credentials: 'include',
                }
            );

            if (!response.ok) {
                if (response.status === 429) {
                    const errorData = await response.json();
                    setExportError(`Rate limit exceeded. ${errorData.retryAfter || 'Please try again later.'}`);
                } else {
                    throw new Error(`Export failed with status ${response.status}`);
                }
                setExportLoading(prev => ({ ...prev, [format]: false }));
                return;
            }

            const blob = await response.blob();
            const contentDisposition = response.headers.get('Content-Disposition');
            const filenameMatch = contentDisposition?.match(/filename="(.+)"/);
            const filename = filenameMatch ? filenameMatch[1] : `user_${userId}_data.${format}`;

            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);

            setLastExport(new Date().toLocaleString());
            await checkExportStatus();
        } catch (error) {
            console.error("Error exporting data:", error);
            setExportError("Failed to export data. Please try again.");
        } finally {
            setExportLoading(prev => ({ ...prev, [format]: false }));
        }
    };

    const renderCategory = (
        title,
        category,
        countField = "angel_count",
        requireOwned = false,
        clearType = null
    ) => {
        // Optionally restrict to angels with a positive count for this field
        const baseList = requireOwned
            ? category.filter((angel) => (angel[countField] ?? 0) > 0)
            : category;

        const filteredAngels = filterAndSortAngels(baseList);

        return (
            <Paper elevation={6} sx={angelCategoryStyles}>
                <Typography variant="h5" gutterBottom sx={angelTypographyStyles}>
                    {title}
                </Typography>
                {filteredAngels.length === 0 ? (
                    <Typography variant="body2" sx={{ textAlign: "left", color: "#555" }}>
                        No angels here yet.
                    </Typography>
                ) : (
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
                        {filteredAngels.map((angel) => (
                            <SonnyAngelCard
                                key={angel.angels_id}
                                id={angel.angels_id}
                                name={angel.angels_name}
                                imageColorUrl={angel.angels_image_url}
                                imageBwUrl={angel.angels_image_bw_url}
                                imageOpacityUrl={angel.angels_image_opacity_url}
                                count={angel[countField] ?? 0}
                                isFavorite={angel.is_favorite}
                                inSearchOf={angel.in_search_of}
                                willingToTrade={angel.willing_to_trade}
                                onCountChange={(newCount) =>
                                    countField === "trade_count"
                                        ? handleTradeCountChange(angel.angels_id, newCount)
                                        : handleCountChange(angel.angels_id, newCount)
                                }
                                onBookmarkAdd={(type) => handleBookmarkAdd(type, angel.angels_id)}
                                onClearStatus={
                                    clearType
                                        ? () => handleBookmarkAdd(clearType, angel.angels_id)
                                        : undefined
                                }
                            />
                        ))}
                    </Box>
                )}
            </Paper>
        );
    };

    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <Box p={2} sx={{ backgroundImage: "url('/src/assets/AngelArchiveBackground4.jpg')",
            backgroundSize: "100% auto",
            backgroundPosition: "center",
            backgroundRepeat: "repeat",
            padding: "20px",
            minHeight: "100vh" }}>
            {/* Welcome Message */}
            <Typography 
                variant="h4" 
                gutterBottom 
                sx={{ 
                    color: "white", 
                    textAlign: "left", 
                    fontWeight: "bold", 
                    fontSize: "2rem", 
                    textShadow: "2px 2px 8px rgba(0, 0, 0, 0.7)", 
                    marginBottom: "16px" 
                }}
            >
                Welcome, {username ? username : "User"}!
            </Typography>

            <Box
                sx={{
                    display: "flex",
                    flexDirection: { xs: "column", md: "row" },
                    gap: 3,
                    alignItems: "flex-start",
                }}
            >
                {/* Left Side - Export Data and Filter Panel */}
                <Box
                    sx={{
                        width: { xs: "100%", md: 320 },
                        flexShrink: 0,
                        height: "fit-content",
                        alignSelf: "flex-start",
                        position: { md: "sticky" },
                        top: { md: "20px" },
                    }}
                >
                    {/* Export Data Section */}
                    <Paper elevation={6} sx={{
                        ...angelCategoryStyles,
                        marginBottom: "20px"
                    }}>
                        <Typography variant="h5" gutterBottom sx={angelTypographyStyles}>
                            Export Your Data
                        </Typography>
                        <Typography variant="body2" sx={{ marginBottom: "16px", color: "#555" }}>
                            Download your collection data and activity history. Exports are limited to once per hour.
                        </Typography>

                        <Grid container spacing={2} justifyContent="center" alignItems="center">
                            <Grid item xs={12} sm={6} md={12}>
                                <Button
                                    variant="contained"
                                    color="primary"
                                    fullWidth
                                    onClick={() => handleExport('json')}
                                    disabled={exportLoading.json || exportLoading.csv || (exportStatus && !exportStatus.canExport)}
                                    sx={{
                                        padding: "10px 20px",
                                        fontWeight: "600"
                                    }}
                                >
                                    {exportLoading.json ? (
                                        <CircularProgress size={24} color="inherit" />
                                    ) : (
                                        "Download JSON"
                                    )}
                                </Button>
                            </Grid>
                            <Grid item xs={12} sm={6} md={12}>
                                <Button
                                    variant="contained"
                                    color="secondary"
                                    fullWidth
                                    onClick={() => handleExport('csv')}
                                    disabled={exportLoading.json || exportLoading.csv || (exportStatus && !exportStatus.canExport)}
                                    sx={{
                                        padding: "10px 20px",
                                        fontWeight: "600"
                                    }}
                                >
                                    {exportLoading.csv ? (
                                        <CircularProgress size={24} color="inherit" />
                                    ) : (
                                        "Download CSV"
                                    )}
                                </Button>
                            </Grid>
                        </Grid>

                        {exportError && (
                            <Typography variant="body2" sx={{ marginTop: "12px", color: "#d32f2f", fontWeight: "500" }}>
                                {exportError}
                            </Typography>
                        )}

                        {exportStatus && !exportStatus.canExport && (
                            <Typography variant="body2" sx={{ marginTop: "12px", color: "#f57c00", fontWeight: "500" }}>
                                Next export available in {exportStatus.timeRemaining} minutes
                            </Typography>
                        )}

                        {lastExport && (
                            <Typography variant="body2" sx={{ marginTop: "12px", color: "#555", fontStyle: "italic" }}>
                                Last export: {lastExport}
                            </Typography>
                        )}
                    </Paper>

                    {/* Filter Panel */}
                    <Box
                        sx={{
                            bgcolor: "rgba(255,255,255,0.9)",
                            borderRadius: 2,
                            boxShadow: 2,
                            p: 2,
                        }}
                    >
                        <SearchBar options={allProfileAngelNames} onSearch={handleSearch} />
                        <Box mt={2}>
                            <Filter onFilterChange={setFilters} />
                        </Box>
                    </Box>
                </Box>

                {/* Right Side - Content */}
                <Box sx={{ flexGrow: 1 }}>
                    {renderCategory("Here are the angels you've collected:", angels, "angel_count", true, null)}
                    {renderCategory("Your Favorite Angels:", favorites, "angel_count", false, "FAV")}
                    {renderCategory("Angels You're In Search Of:", inSearchOf, "angel_count", false, "ISO")}
                    {renderCategory("Angels You're Willing To Trade:", willingToTrade, "trade_count", false, "WTT")}
                </Box>
            </Box>
        </Box>
    );
};

