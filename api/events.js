export default (req, res) => {
  res.status(200).json({
    status: "live",
    events: [
      { id: 1, name: "Test Event" }
    ]
  });
};
