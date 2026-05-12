module.exports = {
  apps: [
    {
      name: "redline-os",
      script: "streamlit",
      args: "run app.py --server.port 8501 --server.address 0.0.0.0",
      interpreter: "venv/bin/python3",
      env: {
        PYTHONPATH: "."
      }
    }
  ]
};
