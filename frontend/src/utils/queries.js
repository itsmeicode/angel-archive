import api from "../services/api";

export async function fetchAngelsProfileImages() {
    try {
        const data = await api.angels.getProfilePics();
        if (!Array.isArray(data)) {
            console.error("Expected array but got:", typeof data, data);
            return [];
        }
        return data.sort((a, b) => a.name.localeCompare(b.name));
    } catch (error) {
        console.error("Error fetching angels data:", error);
        return [];
    }
}

export async function fetchAngelsImages() {
    try {
        const data = await api.angels.getAll();
        if (!Array.isArray(data)) {
            console.error("Expected array but got:", typeof data, data);
            return [];
        }
        const sortedData = data.sort((a, b) => a.name.localeCompare(b.name));

        return sortedData.map(angel => ({
            id: angel.id,
            name: angel.name,
            image_bw: angel.image_bw,
            image: angel.image,
            image_opacity: angel.image_opacity,
            image_bw_url: angel.image_bw_url,
            image_url: angel.image_url,
            image_opacity_url: angel.image_opacity_url,
        }));
    } catch (error) {
        console.error("Error fetching angel images:", error);
        return [];
    }
}

export const createUserInDatabase = async (userData) => {
    try {
        const data = await api.auth.createUser(userData);
        return data;
    } catch (error) {
        console.error("Error inserting user into database:", error);
        return null;
    }
};
