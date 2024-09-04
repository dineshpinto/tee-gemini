// SPDX-License-Identifier: MIT
// Import ownable from OpenZeppelin
import "@openzeppelin/contracts/access/Ownable.sol";
pragma solidity ^0.8.6;

contract Interactor is Ownable {
    struct OIDCRequest {
        address sender;
        uint256 uid;
        string data;
    }

    struct Request {
        address sender;
        uint256 uid;
        string data; // TODO: This should be bytes, but keep it as string for simplicity
    }

    struct Response {
        uint256 uid; // Response uid
        string text;
        uint256 promptTokenCount;
        uint256 candidateTokenCount;
        uint256 totalTokenCount;
    }

    event OIDCRequestSubmitted(uint256 uid, address sender);
    event OIDCRequestFullfilled(uint256 uid, string data);

    event RequestSubmitted(uint256 uid, address sender, string data);
    event RequestFullfilled(
        uint256 uid,
        string text,
        uint256 promptTokenCount,
        uint256 candidateTokenCount,
        uint256 totalTokenCount
    );

    Request[] public requests;
    OIDCRequest[] public oidcRequests;
    mapping(uint256 => Response) public responses;
    bytes32 public ekPublicKey;

    constructor(bytes32 _ekPublicKey) Ownable() {
        ekPublicKey = _ekPublicKey;
    }

    function getEkAddress() external view returns (address) {
        return address(bytes20(keccak256(abi.encode(ekPublicKey))));
    }

    function setEkPublicKey(bytes32 _ekPublicKey) external onlyOwner {
        ekPublicKey = _ekPublicKey;
    }

    function requestOIDCToken() external returns (uint256) {
        uint256 uid = oidcRequests.length + 1;
        OIDCRequest memory req = OIDCRequest({
            sender: msg.sender,
            uid: uid,
            data: ""
        });
        oidcRequests.push(req);
        emit OIDCRequestSubmitted(uid, msg.sender);
        return uid;
    }

    function fulfillOIDCToken(uint256 _uid, string memory _data) external {
        // This would be limited to the address of eligible fulfillers

        emit OIDCRequestFullfilled(_uid, _data);
    }

    function makeRequest(string memory _data) external {
        uint256 uid = requests.length + 1;
        Request memory req = Request({
            sender: msg.sender,
            uid: uid,
            data: _data
        });
        requests.push(req);
        emit RequestSubmitted(uid, msg.sender, _data);
    }

    function fulfillRequest(uint256 _uid, Response memory _response) external {
        // This would be limited to the address of eligible fulfillers

        require(responses[_uid].uid == 0, "Response already exists");

        responses[_uid] = _response;

        emit RequestFullfilled(
            _uid,
            _response.text,
            _response.promptTokenCount,
            _response.candidateTokenCount,
            _response.totalTokenCount
        );
    }

    function getRequestsCount() external view returns (uint256) {
        return requests.length;
    }

    function getRequests() external view returns (Request[] memory) {
        Request[] memory result = new Request[](requests.length);
        for (uint256 i = 0; i < requests.length; i++) {
            result[i] = requests[i];
        }
        return result;
    }

    function getResponses() public view returns (Response[] memory) {
        Response[] memory result = new Response[](requests.length);
        for (uint256 i = 0; i < requests.length; i++) {
            result[i] = responses[i];
        }
        return result;
    }

    function getLatestResponse() public view returns (Response memory) {
        return responses[requests.length];
    }

    function getOIDCRequestsCount() external view returns (uint256) {
        return oidcRequests.length;
    }

    function getOIDCRequests() external view returns (OIDCRequest[] memory) {
        OIDCRequest[] memory result = new OIDCRequest[](oidcRequests.length);
        for (uint256 i = 0; i < oidcRequests.length; i++) {
            result[i] = oidcRequests[i];
        }
        return result;
    }
}
