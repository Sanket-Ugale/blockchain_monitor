module.exports = {
  networks: {
    ganache: {
      host: "127.0.0.1",
      port: 7545,
      network_id: "*"
    }
  },
  compilers: {
    solc: {
      version: "0.8.21", // Must match your pragma
      settings: {
        evmVersion: "london" // Explicit EVM version
      }
    }
  }
};