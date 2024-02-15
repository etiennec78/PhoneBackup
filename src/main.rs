use adb_client::AdbTcpConnexion;
use std::net::Ipv4Addr;

fn main() {
    let mut connexion = AdbTcpConnexion::new(Ipv4Addr::from([192,168,0,64]), 39979).unwrap();
    let devices_result = connexion.devices();

    match devices_result {
        Ok(devices) => {
            println!("Devices: {:#?}", devices);
        }
        Err(error) => {
            println!("Error: {:?}", error);
        }
    }
}
