use std::{io, net::{IpAddr, TcpStream}};
use ssh2::Session;

#[derive(Debug,Eq,PartialEq)]
pub struct SessionProvider {
    target: IpAddr
}

impl SessionProvider {

    pub fn new(target: IpAddr) -> SessionProvider {
        SessionProvider {
            target
        }
    }

    pub fn provide(&self) -> Result<Session, io::Error> {
        let stream: TcpStream = TcpStream::connect(self.target)?;
        let mut session: Session = Session::new()?;
        session.set_tcp_stream(stream);
        session.handshake()?;
        Ok(session)
    }

    pub fn authenticate(session: &mut Session, username: &str) -> Result<(), io::Error> {
        session.userauth_agent("username")?;
        Ok(())
    }

}
