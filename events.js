// Simple test API
export default (req, res) => {
  res.json({
    status: "success",
    region: "IND",
    events: [
      {
        title: "TEST EVENT 1",
        banner: "https://i.imgur.com/6Q9Z8Zl.png" // Sample image
      }
    ]
  });
};