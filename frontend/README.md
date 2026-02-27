# DataSage Frontend

React frontend for the DataSage Conversational Data Intelligence Platform.

## Features

✅ Premium dark neo-enterprise theme (black + gold)
✅ Animated glassmorphic UI components
✅ CSV drag-and-drop upload interface
✅ Real-time dataset preview and schema detection
✅ Natural language query interface
✅ 4-section structured response display
✅ Dynamic chart rendering (Bar, Pie, Line, KPI)
✅ Confidence scoring visualization
✅ Data grounding badges
✅ Responsive design

## Tech Stack

- **React 18.2** - UI library
- **Vite** - Build tool and dev server
- **Framer Motion** - Animations
- **Recharts** - Chart library
- **Axios** - HTTP client
- **React Router** - Navigation

## Design System

### Colors

- Background: `#0C0E14`
- Accent Gold: `#EAAB00`
- Text Primary: `#FFFFFF`
- Text Secondary: `#B4B8C5`

### Typography

- **DM Sans** - Body text
- **Lora** - Headings
- **DM Mono** - Code & data

## Setup

```bash
# Install dependencies
npm install

# Run development server (port 3000)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
src/
├── pages/
│   ├── LandingPage.jsx          # Home with CSV upload
│   ├── LandingPage.css
│   ├── DashboardPage.jsx        # Main dashboard
│   └── DashboardPage.css
├── components/
│   ├── QueryTab.jsx             # Query interface
│   ├── QueryTab.css
│   ├── ChartComponent.jsx       # Visualization
│   ├── ChartComponent.css
│   ├── ConfidenceComponent.jsx  # Confidence UI
│   ├── ConfidenceComponent.css
│   ├── DatasetInfoPanel.jsx     # Dataset summary
│   └── DatasetInfoPanel.css
├── App.jsx                      # Router
├── main.jsx                     # Entry point
└── index.css                    # Global styles
```

## API Integration

Backend URL: `http://localhost:8000`

Proxy configured in `vite.config.js`:

```javascript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true
  }
}
```

## Key Components

### LandingPage

- CSV file upload with drag-and-drop
- File validation
- Dataset preview with schema
- Animated transitions

### DashboardPage

- Tab navigation (Query, Overview, Insights)
- Dataset info badge
- Context-aware routing

### QueryTab (Most Important)

- Natural language input
- Suggested questions
- Loading states
- **4-section response display:**
  1. Natural Answer
  2. SQL Logic
  3. Derivation
  4. Visualization
- Confidence scoring
- Data grounding badge

### ChartComponent

- Bar charts (grouped data)
- Pie/Doughnut charts (distributions)
- Line charts (time series)
- KPI cards (single metrics)

### ConfidenceComponent

- Animated progress bar
- Color-coded levels (high/medium/low)
- Confidence score display

### DatasetInfoPanel

- Row/column counts
- Schema breakdown
- Active dataset indicator

## Styling Guidelines

### Glassmorphic Cards

```css
background: rgba(26, 29, 43, 0.6);
backdrop-filter: blur(20px);
border: 1px solid rgba(234, 171, 0, 0.2);
border-radius: 16px;
```

### Buttons

```css
/* Primary */
background: linear-gradient(135deg, #eaab00, #ffd700);

/* Secondary */
border: 2px solid #eaab00;
background: transparent;
```

### Animations

All page transitions use Framer Motion:

```jsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.5 }}
>
```

## Development Tips

1. **Hot Module Replacement** - Changes reflect instantly
2. **Component-scoped CSS** - Each component has its own CSS file
3. **Responsive Design** - Mobile breakpoint at 768px
4. **Error Boundaries** - Add for production
5. **Loading States** - Always show feedback during async operations

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance

- Lazy loading for route components
- Optimized Recharts rendering
- CSS-only animations where possible
- Vite's built-in code splitting

## Deployment

```bash
# Build for production
npm run build

# Output in dist/ folder
# Deploy to Netlify, Vercel, or any static host
```

## Environment Variables

Create `.env.local`:

```
VITE_API_URL=http://localhost:8000
```

Access in code:

```javascript
const API_URL = import.meta.env.VITE_API_URL;
```

## Troubleshooting

**Issue:** CORS errors
**Fix:** Ensure backend has CORS middleware enabled

**Issue:** Charts not rendering
**Fix:** Check that chart data follows Recharts format

**Issue:** Styles not loading
**Fix:** Verify CSS imports in component files

## Contributing

Follow the project's component structure and styling patterns. Use functional components with hooks.

## License

MIT
