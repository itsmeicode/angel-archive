import React, { useState, useEffect } from "react";
import { AppBar, Toolbar, Typography, Box, IconButton, Avatar, Menu, MenuItem } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import api from "../src/services/api";

const sectionStyle = {
    display: "flex",
    alignItems: "center",
};

export function NavBarDashboard() {
    const { signOut } = useAuth();
    const navigate = useNavigate();
    const { user } = useAuth();
    const [profilePic, setProfilePic] = useState(null);
    const [anchorEl, setAnchorEl] = useState(null);
    const open = Boolean(anchorEl);

    useEffect(() => {
        const fetchProfilePic = async () => {
            if (!user?.id) return;

            try {
                const data = await api.users.getProfile(user.id);
                setProfilePic(data?.profile_pic);
            } catch (err) {
                console.error("Error fetching profile pic:", err);
            }
        };

        fetchProfilePic();
    }, [user]);

    const handleMenuOpen = (event) => setAnchorEl(event.currentTarget);
    const handleClose = () => setAnchorEl(null);

    const handleLogoClick = () => {
        navigate(user ? "/dashboard" : "/");
    };

    return (
        <AppBar position="sticky">
            <Toolbar
                sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    height: { xs: "auto", sm: "80px" },
                }}
            >
                <Box display="flex" alignItems="center" onClick={handleLogoClick} style={{ cursor: "pointer" }}>
                    <img 
                        src="../src/assets/AngelArchiveLogo.png" 
                        alt="Angel Archive Logo" 
                        style={{ width: "73px", height: "80px", marginRight: "12px", objectFit: "contain" }} 
                    />
                    <Typography 
                        variant="h6" 
                        sx={{ fontSize: "1.875rem", fontWeight: "bold", display: "flex", alignItems: "center" }}
                    >
                        Angel Archive 
                    </Typography>
                </Box>
                
                <Box sx={{ ...sectionStyle }}>
                    <IconButton onClick={handleMenuOpen}>
                        <Avatar
                            src={profilePic || "/default-profile.png"} 
                            alt="Profile"
                            loading="lazy"
                            sx={{ width: "60px", height: "60px" }}
                        />
                    </IconButton>

                    <Menu
                        id="profile-menu"
                        anchorEl={anchorEl}
                        open={open}
                        onClose={handleClose}
                        anchorOrigin={{ vertical: "top", horizontal: "right" }}
                        transformOrigin={{ vertical: "top", horizontal: "right" }}
                    >
                        <MenuItem onClick={() => { 
                            handleClose(); 
                            navigate("/profile"); 
                        }}>
                            Profile
                        </MenuItem>                        
                        <MenuItem onClick={signOut}>
                            Log Out
                        </MenuItem>
                    </Menu>
                </Box>
            </Toolbar>
        </AppBar>
    );
}

