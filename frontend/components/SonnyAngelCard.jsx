import { useMemo, useState } from "react";
import { Counter } from "./Counter";
import "../src/App.css";

export function SonnyAngelCard({
  id,
  name,
  imageBwUrl,
  imageOpacityUrl,
  imageColorUrl,
  onBookmarkAdd,
  count,
  onCountChange,
  onClearStatus,
  isFavorite,
  inSearchOf,
  willingToTrade,
}) {
  const [showBookmarkOptions, setShowBookmarkOptions] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  const handleBookmarkClick = (type) => {
    onBookmarkAdd(type, id, name);
  };

  const displayImageUrl = useMemo(() => {
    const owned = (Number(count) || 0) > 0;

    // Owned: show full-color
    if (owned) return imageColorUrl || imageBwUrl || imageOpacityUrl;

    // Not owned: default BW; on hover show opacity variant
    if (isHovered) return imageOpacityUrl || imageBwUrl;
    return imageBwUrl || imageOpacityUrl;
  }, [count, imageBwUrl, imageColorUrl, imageOpacityUrl, isHovered]);

  return (
    <div
      className="sonny-angel-card"
      onMouseEnter={() => {
        setShowBookmarkOptions(true);
        setIsHovered(true);
      }}
      onMouseLeave={() => {
        setShowBookmarkOptions(false);
        setIsHovered(false);
      }}
    >
      <p className="name">{name}</p>

      {onClearStatus && (
        <button
          type="button"
          className="sonny-angel-clear-btn"
          onClick={onClearStatus}
        >
          ×
        </button>
      )}

      <img src={displayImageUrl} alt={name} loading="lazy" className="image" />

      {showBookmarkOptions && (
        <div className="bookmark-options">
          {["FAV", "ISO", "WTT"].map((type) => (
            <button
              key={type}
              className="bookmark-btn"
              onClick={() => handleBookmarkClick(type)}
            >
              {type}
            </button>
          ))}
        </div>
      )}

      <Counter count={count} onChange={onCountChange} />

      {(isFavorite || inSearchOf || willingToTrade) && (
        <div className="sonny-angel-status-strip">
          {isFavorite && <span className="status-icon status-fav" title="Favorite">💖</span>}
          {inSearchOf && <span className="status-icon status-iso" title="In search of">🔍</span>}
          {willingToTrade && <span className="status-icon status-wtt" title="Willing to trade">🤝</span>}
        </div>
      )}
    </div>
  );
}

