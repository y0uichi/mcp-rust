use super::*;
use std::cell::RefCell;
use std::rc::Rc;

#[derive(Debug)]
enum MockError {}

struct MockTransport {
    history: Rc<RefCell<Vec<JsonRpcMessage>>>,
    started: bool,
    closed: bool,
}

impl MockTransport {
    fn new(history: Rc<RefCell<Vec<JsonRpcMessage>>>) -> Self {
        Self {
            history,
            started: false,
            closed: false,
        }
    }
}

impl Transport for MockTransport {
    type Message = JsonRpcMessage;
    type Error = MockError;

    fn start(&mut self) -> Result<(), Self::Error> {
        self.started = true;
        Ok(())
    }

    fn send(&mut self, message: &Self::Message) -> Result<(), Self::Error> {
        self.history.borrow_mut().push(message.clone());
        Ok(())
    }

    fn close(&mut self) -> Result<(), Self::Error> {
        self.closed = true;
        Ok(())
    }
}

#[test]
fn handshake_is_sent_after_start() {
    let history = Rc::new(RefCell::new(Vec::new()));
    let transport = MockTransport::new(Rc::clone(&history));
    let mut client = Client::new(transport, ClientOptions::new("rust-client"));

    client.start().unwrap();
    client.handshake().unwrap();
    client.close().unwrap();

    let sent = history.borrow();
    assert_eq!(sent.len(), 1);
    if let JsonRpcMessage::Request(req) = &sent[0] {
        assert_eq!(req.method, "client/hello");
        assert_eq!(req.params["serviceName"], "rust-client");
    } else {
        panic!("expected a request");
    }
}

#[test]
fn request_can_be_sent() {
    let history = Rc::new(RefCell::new(Vec::new()));
    let transport = MockTransport::new(Rc::clone(&history));
    let mut client = Client::new(transport, ClientOptions::new("rust-client"));

    client.start().unwrap();
    client.handshake().unwrap();
    client
        .send_request("tools/list", serde_json::json!({}))
        .unwrap();

    let sent = history.borrow();
    assert_eq!(sent.len(), 2);
    if let JsonRpcMessage::Request(req) = &sent[1] {
        assert_eq!(req.method, "tools/list");
    } else {
        panic!("expected a request");
    }
}
