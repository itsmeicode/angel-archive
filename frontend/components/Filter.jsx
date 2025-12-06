import React, { useState } from "react";
import { Box, Typography, FormControl, InputLabel, Select, MenuItem, Checkbox, Button } from "@mui/material";

const inventoryOptions = [
  "Select All",
  "All in inventory",
  "All not in inventory",
];

const seriesOptions = [
  "Animal 1 2018 Series",
  "Animal 2 2018 Series",
  "Animal 3 2018 Series",
  "Animal 4 2018 Series",
  "Animal 1 Series",
  "Animal 2 Series",
  "Animal 3 Series",
  "Animal 4 Series",
  "Flower 2019 Series",
  "Fruit 2019 Series",
  "Fruit Series",
  "Marine 2019 Series",
  "Marine Series",
  "Sweets 2018 Series",
  "Sweets Series",
  "Vegetable 2019 Series",
];

const statusOptions = ["FAV - Favorite", "ISO - In Search Of", "WTT - Willing To Trade"];

export function Filter({ onFilterChange }) {
  const [inventory, setInventory] = useState("");
  const [selectedSeries, setSelectedSeries] = useState([]);
  const [selectedStatus, setSelectedStatus] = useState([]);

  const handleInventoryChange = (event) => {
    const newInventory = event.target.value;
    setInventory(newInventory);
    onFilterChange({ inventory: newInventory, series: selectedSeries, status: selectedStatus });
  };

  const handleSeriesChange = (event) => {
    const newSeries = event.target.value;
    setSelectedSeries(newSeries);
    onFilterChange({ inventory, series: newSeries, status: selectedStatus });
  };

  const handleStatusChange = (event) => {
    const newStatus = event.target.value;
    setSelectedStatus(newStatus);
    onFilterChange({ inventory, series: selectedSeries, status: newStatus });
  };

  const resetFilters = () => {
    setInventory("");
    setSelectedSeries([]);
    setSelectedStatus([]);
    onFilterChange({ inventory: "", series: [], status: [] });
  };

  return (
    <Box sx={{ padding: "20px" }}>
      <Typography variant="h5" gutterBottom>Filter Options</Typography>

      <FormControl fullWidth sx={{ marginBottom: "20px" }}>
        <InputLabel>Inventory Status</InputLabel>
        <Select
          value={inventory}
          label="Inventory Status"
          onChange={handleInventoryChange}
        >
          {inventoryOptions.map((option) => (
            <MenuItem key={option} value={option}>
              {option}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <FormControl fullWidth sx={{ marginBottom: "20px" }}>
        <InputLabel>Series</InputLabel>
        <Select
          multiple
          value={selectedSeries}
          label="Series"
          onChange={handleSeriesChange}
          renderValue={(selected) => selected.join(", ")}
          MenuProps={{
            PaperProps: {
              style: {
                width: "400px",
                maxHeight: "300px",
              },
            },
          }}
        >
          {seriesOptions.map((option) => (
            <MenuItem key={option} value={option}>
              <Checkbox checked={selectedSeries.indexOf(option) > -1} />
              {option}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <FormControl fullWidth sx={{ marginBottom: "20px" }}>
        <InputLabel>Status</InputLabel>
        <Select
          multiple
          value={selectedStatus}
          label="Status"
          onChange={handleStatusChange}
          renderValue={(selected) => selected.join(", ")}
          MenuProps={{
            PaperProps: {
              style: {
                width: "200px", 
                maxHeight: "300px",
              },
            },
          }}
        >
          {statusOptions.map((option) => (
            <MenuItem key={option} value={option}>
              <Checkbox checked={selectedStatus.indexOf(option) > -1} />
              {option}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <Button variant="outlined" onClick={resetFilters}>
        Reset Filters
      </Button>
    </Box>
  );
}

