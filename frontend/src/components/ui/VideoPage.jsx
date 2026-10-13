export default function VideoPage({ className = "", children }) {
  return (
    <main className={`video-page ${className}`}>
      <video
        className="page-video"
        src="/videos/robot-friendship-background.mp4"
        autoPlay
        muted
        loop
        playsInline
        aria-hidden="true"
      />
      <div className="page-video-overlay" />
      <div className="page-content">{children}</div>
    </main>
  );
}
