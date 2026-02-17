import React, { useEffect, useState } from "react";
import { Box, Grid, Typography, useMediaQuery, Paper, Button, CircularProgress } from "@mui/material";
import { SonnyAngelCard } from "../components/SonnyAngelCard";
import { SearchBar } from "../components/SearchBar";
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

    const fetchAngelDetails = async (angels) => {
        return Promise.all(
            angels.map(async (angel) => {
                const angelDetails = await api.angels.getById(angel.id);
                return {
                    angels_id: angel.id,
                    angels_name: angelDetails?.name,
                    angels_image_url: angelDetails?.image_url,
                    angel_count: angel.count,
                };
            })
        );
    };

    useEffect(() => {
        const fetchUserAndCollections = async () => {
            const { user } = await api.auth.getUser();
            if (user) {
                setUserId(user.id);
                const userData = await api.users.getProfile(user.id);
                setUsername(userData?.username);

                const collections = await api.collections.getByUser(user.id);

                if (collections) {
                    const categories = {
                        favorites: [],
                        inSearchOf: [],
                        willingToTrade: [],
                        allAngels: [],
                    };

                    collections.forEach((collection) => {
                        const angelData = {
                            angels_id: collection.angels.id,
                            angels_name: collection.angels.name,
                            angels_image_url: collection.angels.image_url,
                            angels_image_bw_url: collection.angels.image_bw_url,
                            angels_image_opacity_url: collection.angels.image_opacity_url,
                            angel_count: collection.count,
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
                }

                await checkExportStatus();
            }
            setLoading(false);
        };

        fetchUserAndCollections();
    }, []);

    const handleSearch = (searchTerm) => {
        setSearchTerm(searchTerm.toLowerCase());
    };

    const filterAngels = (angels) => {
        return angels.filter((angel) =>
            angel.angels_name.toLowerCase().includes(searchTerm)
        );
    };

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

    const renderCategory = (title, category) => {
        if (category.length === 0) return null;

        const filteredAngels = filterAngels(category);

        if (filteredAngels.length === 0) return null;

        return (
            <Paper elevation={6} sx={angelCategoryStyles}>
                <Typography variant="h5" gutterBottom sx={angelTypographyStyles}>
                    {title}
                </Typography>
                <Grid container spacing={3} justifyContent="flex-start">
                    {filteredAngels.map((angel) => (
                        <Grid item key={angel.angels_id} xs={6} sm={4} md={3} lg={2}>
                            <SonnyAngelCard
                                id={angel.angels_id}
                                name={angel.angels_name}
                                imageColorUrl={angel.angels_image_url}
                                imageBwUrl={angel.angels_image_bw_url}
                                imageOpacityUrl={angel.angels_image_opacity_url}
                                userId={userId}
                                onBookmarkAdd={handleBookmarkAdd}
                                initialCount={angel.angel_count}
                            />
                        </Grid>
                    ))}
                </Grid>
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
            <Typography variant="h4" gutterBottom sx={{ color: "white", textAlign: "left", fontWeight: "bold", fontSize: "2.5rem", textShadow: "2px 2px 8px rgba(0, 0, 0, 0.7)", marginBottom: "16px" }}>
                Welcome, {username ? username : "User"}!
            </Typography>

            <SearchBar options={[]} onSearch={handleSearch} />

            <Paper elevation={6} sx={{
                ...angelCategoryStyles,
                marginTop: "20px",
                marginBottom: "20px"
            }}>
                <Typography variant="h5" gutterBottom sx={angelTypographyStyles}>
                    Export Your Data
                </Typography>
                <Typography variant="body2" sx={{ marginBottom: "16px", color: "#555" }}>
                    Download your collection data and activity history. Exports are limited to once per hour.
                </Typography>

                <Grid container spacing={2} justifyContent="center" alignItems="center">
                    <Grid item xs={12} sm={6} md={3}>
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
                    <Grid item xs={12} sm={6} md={3}>
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

            {renderCategory("Here are the angels you've collected:", angels)}
            {renderCategory("Your Favorite Angels:", favorites)}
            {renderCategory("Angels You're In Search Of:", inSearchOf)}
            {renderCategory("Angels You're Willing To Trade:", willingToTrade)}
        </Box>
    );
};

