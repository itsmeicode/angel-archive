import React, { useState } from 'react';
import { MenuItem, FormControl, Select, InputLabel, Grid, Typography } from '@mui/material';

const items = [
  { name: 'Banana', count: 12 },
  { name: 'Apple', count: 5 },
  { name: 'Orange', count: 8 },
  { name: 'Mango', count: 20 },
  { name: 'Pineapple', count: 3 }
];

export function Sort() {
  const [sortOrder, setSortOrder] = useState('asc'); 
  const [sortedItems, setSortedItems] = useState(items); 

  const handleSortChange = (event) => {
    const newSortOrder = event.target.value;
    setSortOrder(newSortOrder);

    let sorted = [...items];
    sorted = sorted.sort((a, b) => {
      if (newSortOrder === 'asc') {
        return a.count - b.count;
      } else {
        return b.count - a.count;
      }
    });

    setSortedItems(sorted);
  };

  return (
    <div style={{ padding: 20 }}>
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6}>
          <FormControl fullWidth>
            <InputLabel>Sort Order</InputLabel>
            <Select
              value={sortOrder}
              onChange={handleSortChange}
              label="Sort Order"
            >
              <MenuItem value="asc">Ascending</MenuItem>
              <MenuItem value="desc">Descending</MenuItem>
            </Select>
          </FormControl>
        </Grid>
      </Grid>

      <div style={{ marginTop: '30px' }}>
        <Typography variant="h6">Sorted Items:</Typography>
        <ul>
          {sortedItems.map((item) => (
            <li key={item.name}>
              {item.name} - {item.count}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

