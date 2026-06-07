function Sidebar({ groups }) {
  return (
    <div className="sidebar">
      <h2>Groups</h2>

      {groups.map((group) => (
        <div key={group.name} className="group-card">
          <h4>{group.name}</h4>
          <small>{group.docs} documents</small>
        </div>
      ))}
    </div>
  );
}

export default Sidebar;