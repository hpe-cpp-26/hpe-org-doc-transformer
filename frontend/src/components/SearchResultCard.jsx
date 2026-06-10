function SearchResultCard({ data, onClick }) {
  return (
    <div className="search-card" onClick={onClick}>
      <h4>{data.title}</h4>

      <p>Source: {data.source}</p>

      <p>Similarity: {data.similarity}</p>
    </div>
  );
}

export default SearchResultCard;