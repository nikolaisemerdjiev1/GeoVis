export default function Section({ title, children }) {
  return (
    <section className="card">
      <div className="section-header">
        <h2>{title}</h2>
      </div>
      {children}
    </section>
  )
}
