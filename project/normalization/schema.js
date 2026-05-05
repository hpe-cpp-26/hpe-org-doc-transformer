function buildNormalizedEvent({ id, source, type, resource, actor, changes, meta }) {
  if (!id || !source || !type || !resource?.name) {
    throw new Error(
      `Normalization error: missing required fields — id=${id}, source=${source}, type=${type}`
    );
  }

  return {
    id,
    source,
    type,
    resource: {
      id: resource.id || id,
      name: resource.name,
      url: resource.url || "",
      status: resource.status || "N/A",
    },
    actor: {
      id: actor?.id || null,
      name: actor?.name || null,
      email: actor?.email || null,
    },
    changes: {
      files: changes?.files || [],
      commits: changes?.commits || [],
      fieldChanges: changes?.fieldChanges || [],
      pageChanges: changes?.pageChanges || null,
      boardChanges: changes?.boardChanges || [],
    },
    meta: meta || {},
    receivedAt: new Date().toISOString(),
  };
}

module.exports = { buildNormalizedEvent };