import { useEffect, useMemo, useState } from "react";
import { Counter } from "./Counter";
import "../src/App.css";

export function SonnyAngelCard({
  id,
  name,
  imageUrl,
  imageBwUrl,
  imageOpacityUrl,
  imageColorUrl,
  onBookmarkAdd,
  userId,
  initialCount,
}) {
  const [showBookmarkOptions, setShowBookmarkOptions] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [count, setCount] = useState(() => (Number.isNaN(Number(initialCount)) ? 0 : Number(initialCount)));

  useEffect(() => {
    const next = Number.isNaN(Number(initialCount)) ? 0 : Number(initialCount);
    setCount(next);
  }, [initialCount]);

  const handleBookmarkClick = (type) => {
    onBookmarkAdd(type, id, name);
  };

  const displayImageUrl = useMemo(() => {
    const owned = (Number(count) || 0) > 0;

    // Owned: prefer full-color (fallback to provided imageUrl)
    if (owned) return imageColorUrl || imageUrl || imageBwUrl || imageOpacityUrl;

    // Not owned: default BW; on hover show opacity variant
    if (isHovered) return imageOpacityUrl || imageUrl || imageBwUrl;
    return imageBwUrl || imageUrl || imageOpacityUrl;
  }, [count, imageBwUrl, imageColorUrl, imageOpacityUrl, imageUrl, isHovered]);

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

      <Counter userId={userId} angelId={id} count={count} onChange={setCount} />
    </div>
  );
}

