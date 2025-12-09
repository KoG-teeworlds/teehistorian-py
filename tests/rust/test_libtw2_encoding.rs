// Test if libtw2 has encoding functions
// Run with: cargo test --lib test_libtw2 -- --nocapture

#[cfg(test)]
mod tests {
    use libtw2_gamenet_ddnet as gamenet;
    use libtw2_packer::Packer;

    #[test]
    fn test_libtw2_encode() {
        // Check if there's an encode method
        // let msg = gamenet::msg::game::ClStartInfo {
        //     ...
        // };

        // Try to encode it
        // msg.encode(...)?

        println!("Checking libtw2 encoding capabilities...");

        // The library should have encoding functions
        // Let's see what's available
    }
}
