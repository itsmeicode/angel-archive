import React, { useEffect, useState } from "react";
import { Box, Typography, FormControl, InputLabel, Select, MenuItem, Checkbox, Button } from "@mui/material";
import { fetchSeries } from "../src/utils/queries";

const inventoryOptions = [
  { value: "all", label: "All angels" },
  { value: "owned", label: "Owned only" },
  { value: "unowned", label: "Unowned only" },
];

const statusOptions = [
  { key: "fav", label: "FAV - Favorite" },
  { key: "iso", label: "ISO - In Search Of" },
  { key: "wtt", label: "WTT - Willing To Trade" },
];

const sortOptions = [
  { value: "name-asc", label: "Name (A-Z)" },
  { value: "name-desc", label: "Name (Z-A)" },
  { value: "count-desc", label: "Count (High to Low)" },
  { value: "count-asc", label: "Count (Low to High)" },
];

export function Filter({ onFilterChange }) {
  const [inventory, setInventory] = useState("all");
  const [seriesOptions, setSeriesOptions] = useState([]);
  const [selectedSeriesIds, setSelectedSeriesIds] = useState([]);
  const [selectedStatusKeys, setSelectedStatusKeys] = useState([]);
  const [sortBy, setSortBy] = useState("name-asc");

  useEffect(() => {
    const load = async () => {
      const series = await fetchSeries();
      setSeriesOptions(series || []);
    };
    load();
  }, []);

  const emitFilters = (next = {}) => {
    const filters = {
      owned: inventory,
      seriesIds: selectedSeriesIds,
      fav: selectedStatusKeys.includes("fav"),
      iso: selectedStatusKeys.includes("iso"),
      wtt: selectedStatusKeys.includes("wtt"),
      sortBy: sortBy,
      ...next,
    };
    onFilterChange?.(filters);
  };

  const handleInventoryChange = (event) => {
    const value = event.target.value;
    setInventory(value);
    emitFilters({ owned: value });
  };

  const handleSeriesChange = (event) => {
    const ids = event.target.value;
    setSelectedSeriesIds(ids);
    emitFilters({ seriesIds: ids });
  };

  const handleStatusChange = (event) => {
    const keys = event.target.value;
    setSelectedStatusKeys(keys);
    emitFilters({
      fav: keys.includes("fav"),
      iso: keys.includes("iso"),
      wtt: keys.includes("wtt"),
    });
  };

  const handleSortChange = (event) => {
    const value = event.target.value;
    setSortBy(value);
    emitFilters({ sortBy: value });
  };

  const resetFilters = () => {
    setInventory("all");
    setSelectedSeriesIds([]);
    setSelectedStatusKeys([]);
    setSortBy("name-asc");
    emitFilters({
      owned: "all",
      seriesIds: [],
      fav: false,
      iso: false,
      wtt: false,
      sortBy: "name-asc",
    });
  };

  return (
    <Box sx={{ padding: "12px", height: "fit-content" }}>
      <Typography variant="h6" gutterBottom sx={{ mb: 1.5, fontSize: "1rem" }}>Filter Angels</Typography>

      <FormControl fullWidth sx={{ marginBottom: "12px" }}>
        <InputLabel>Ownership</InputLabel>
        <Select
          value={inventory}
          label="Ownership"
          onChange={handleInventoryChange}
        >
          {inventoryOptions.map((opt) => (
            <MenuItem key={opt.value} value={opt.value}>
              {opt.label}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <FormControl fullWidth sx={{ marginBottom: "12px" }}>
        <InputLabel>Series</InputLabel>
        <Select
          multiple
          value={selectedSeriesIds}
          label="Series"
          onChange={handleSeriesChange}
          renderValue={(selected) => {
            if (selected.length === 0) return "";
            if (selected.length === 1) {
              const series = seriesOptions.find((s) => s.id === selected[0]);
              return series?.name || "";
            }
            return `${selected.length} series selected`;
          }}
          MenuProps={{
            PaperProps: {
              style: {
                width: "260px",
                maxHeight: "300px",
              },
            },
          }}
        >
          {seriesOptions.map((s) => (
            <MenuItem key={s.id} value={s.id}>
              <Checkbox checked={selectedSeriesIds.indexOf(s.id) > -1} />
              {s.name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <FormControl fullWidth sx={{ marginBottom: "12px" }}>
        <InputLabel>Status</InputLabel>
        <Select
          multiple
          value={selectedStatusKeys}
          label="Status"
          onChange={handleStatusChange}
          renderValue={(selected) => {
            if (selected.length === 0) return "";
            if (selected.length === 1) {
              const opt = statusOptions.find((o) => o.key === selected[0]);
              return opt?.label || "";
            }
            return `${selected.length} statuses selected`;
          }}
          MenuProps={{
            PaperProps: {
              style: {
                width: "260px",
                maxHeight: "300px",
              },
            },
          }}
        >
          {statusOptions.map((opt) => (
            <MenuItem key={opt.key} value={opt.key}>
              <Checkbox checked={selectedStatusKeys.indexOf(opt.key) > -1} />
              {opt.label}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <FormControl fullWidth sx={{ marginBottom: "12px" }}>
        <InputLabel>Sort By</InputLabel>
        <Select
          value={sortBy}
          label="Sort By"
          onChange={handleSortChange}
        >
          {sortOptions.map((opt) => (
            <MenuItem key={opt.value} value={opt.value}>
              {opt.label}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <Button variant="outlined" onClick={resetFilters} fullWidth size="small">
        Reset Filters
      </Button>
    </Box>
  );
}

