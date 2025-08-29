import React from 'react';

const ChatWidget = ({ onSend }) => {
  const [message, setMessage] = React.useState('');
  return (
    <div>
      <input value={message} onChange={e => setMessage(e.target.value)} />
      <button onClick={() => onSend(message)}>Envoyer</button>
    </div>
  );
};

export default ChatWidget; 