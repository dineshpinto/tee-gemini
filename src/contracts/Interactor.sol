// SPDX-License-Identifier: MIT
// Import ownable from OpenZeppelin
pragma solidity ^0.8.6;

contract Interactor {
    struct OIDCRequest {
        address sender;
        uint256 uid;
        string token;
    }

    struct PromptRequest {
        address sender;
        uint256 uid;
        string prompt; // TODO: This should be bytes, but keep it as string for simplicity
    }

    struct PromptResponse {
        uint256 uid; // Response uid
        string response;
        uint256 promptTokenCount;
        uint256 candidateTokenCount;
        uint256 totalTokenCount;
    }

    event OIDCRequestSubmitted(uint256 uid, address sender);
    event OIDCRequestFullfilled(uint256 uid, string token);

    event PromptRequestSubmitted(uint256 uid, address sender, string prompt);
    event PromptRequestFullfilled(
        uint256 uid,
        string response,
        uint256 promptTokenCount,
        uint256 candidateTokenCount,
        uint256 totalTokenCount
    );

    PromptRequest[] public promptRequests;
    OIDCRequest[] public oidcRequests;
    mapping(uint256 => PromptResponse) public promptResponses;
    bytes public ekPublicKey;
    string public modelName;

    mapping(address => bool) public owners;

    modifier onlyOwner() {
        require(owners[msg.sender], "Only owner can call this function");
        _;
    }

    function addOwner(address _owner) external onlyOwner {
        owners[_owner] = true;
    }

    constructor(bytes memory _ekPublicKey) {
        ekPublicKey = _ekPublicKey;
        owners[msg.sender] = true;
    }

    // Sets the EK public key
    function setEkPublicKey(bytes memory _ekPublicKey) external onlyOwner {
        ekPublicKey = _ekPublicKey;
    }

    // Sets the Gemini model used
    function setModelName(string memory _modelName) external onlyOwner {
        modelName = _modelName;
    }

    // Submit an OIDC request
    function requestOIDCToken() external returns (uint256) {
        uint256 uid = oidcRequests.length + 1;
        OIDCRequest memory req = OIDCRequest({
            sender: msg.sender,
            uid: uid,
            token: ""
        });
        oidcRequests.push(req);
        emit OIDCRequestSubmitted(uid, msg.sender);
        return uid;
    }

    // Fulfill an OIDC request
    function fulfillOIDCToken(
        uint256 _uid,
        string memory _token
    ) external onlyOwner {
        // This would be limited to the address of eligible fulfillers
        emit OIDCRequestFullfilled(_uid, _token);
    }

    // Submit a prompt request
    function makePromptRequest(string memory _prompt) external {
        require(
            bytes(_prompt).length == 0,
            "Request should have a non-zero length"
        );
        uint256 uid = promptRequests.length + 1;
        PromptRequest memory req = PromptRequest({
            sender: msg.sender,
            uid: uid,
            prompt: _prompt
        });
        promptRequests.push(req);
        emit PromptRequestSubmitted(uid, msg.sender, _prompt);
    }

    // Fulfill a prompt request
    function fulfillPromptRequest(
        uint256 _uid,
        PromptResponse memory _res
    ) external onlyOwner {
        require(promptResponses[_uid].uid == 0, "Response already exists");
        promptResponses[_uid] = _res;

        emit PromptRequestFullfilled(
            _uid,
            _res.response,
            _res.promptTokenCount,
            _res.candidateTokenCount,
            _res.totalTokenCount
        );
    }

    // Getter for the number of prompt requests
    function getPromptRequestsCount() external view returns (uint256) {
        return promptRequests.length;
    }

    // Getter for prompt requests
    function getPromptRequests()
        external
        view
        returns (PromptRequest[] memory)
    {
        return promptRequests;
    }

    // Getter for all prompt responses
    function getPromptResponses()
        public
        view
        returns (PromptResponse[] memory)
    {
        PromptResponse[] memory result = new PromptResponse[](
            promptRequests.length
        );
        for (uint256 i = 0; i < promptRequests.length; i++) {
            result[i] = promptResponses[i];
        }
        return result;
    }

    // Getter for the number of OIDC requests
    function getOIDCRequestsCount() external view returns (uint256) {
        return oidcRequests.length;
    }

    // Getter for OIDC requests
    function getOIDCRequests() external view returns (OIDCRequest[] memory) {
        return oidcRequests;
    }

    // Retrieve the latest prompt response
    function getLatestPromptResponse()
        public
        view
        returns (PromptResponse memory)
    {
        require(promptRequests.length > 0, "No prompt requests available");
        return promptResponses[promptRequests.length];
    }
}
