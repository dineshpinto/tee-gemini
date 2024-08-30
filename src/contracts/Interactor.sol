// SPDX-License-Identifier: MIT

pragma solidity ^0.8.6;

contract Interactor {
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

    event RequestSubmitted(uint256 uid, address sender, string data);
    event RequestFullfilled(
        uint256 uid,
        string text,
        uint256 promptTokenCount,
        uint256 candidateTokenCount,
        uint256 totalTokenCount
    );

    Request[] public requests;
    mapping(uint256 => Response) public responses;

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
}
