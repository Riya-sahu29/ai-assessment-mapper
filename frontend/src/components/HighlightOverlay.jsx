export default function HighlightOverlay({ box, colorClass }) {
  if (!box) return null
  return (
    <div
      className={`absolute border-2 rounded-sm transition-all duration-300 pointer-events-none ${colorClass.bg} ${colorClass.border}`}
      style={{
        left: `${box.x_pct}%`,
        top: `${box.y_pct}%`,
        width: `${box.width_pct}%`,
        height: `${box.height_pct}%`,
      }}
    />
  )
}