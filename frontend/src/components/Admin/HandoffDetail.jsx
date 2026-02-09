import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Card, Timeline, Button, Tag, Spin, Empty, message as antMessage,
  Descriptions, Input, Space, Divider, Modal
} from 'antd';
import {
  ArrowLeftOutlined, RobotOutlined, UserOutlined, SendOutlined,
  CheckCircleOutlined, PlayCircleOutlined, UserSwitchOutlined
} from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import { chatAPI } from '../../services/api';
import styles from './HandoffDetail.module.css';
import { formatUTCDateTimeCN } from '../../utils/timeUtils';

const { TextArea } = Input;

const HandoffDetail = () => {
  const { handoffId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [handoff, setHandoff] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [customer, setCustomer] = useState(null);
  const [replyContent, setReplyContent] = useState('');
  const [agentName, setAgentName] = useState('');
  const [takeoverModalVisible, setTakeoverModalVisible] = useState(false);
  const [tempAgentName, setTempAgentName] = useState('');

  const fetchHandoffDetail = async () => {
    try {
      setLoading(true);
      // Get handoff details
      const handoffsRes = await chatAPI.getHandoffs();
      const handoffData = handoffsRes.data.handoffs.find(h => h.id === parseInt(handoffId));

      if (!handoffData) {
        antMessage.error('Handoff record does not exist');
        navigate('/admin/handoffs');
        return;
      }

      setHandoff(handoffData);
      setCustomer(handoffData.customer);

      // Get conversation history - Fixed: Use conversation_id instead of customer_id
      const convRes = await chatAPI.getConversation(handoffData.conversation_id);
      // Wrap single conversation in array to maintain compatibility with original rendering logic
      setConversations(convRes.data ? [convRes.data] : []);
    } catch (error) {
      console.error('Failed to fetch details:', error);
      antMessage.error('Failed to fetch details');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHandoffDetail();
  }, [handoffId]);

  const handleSendReply = async () => {
    if (!replyContent.trim()) {
      antMessage.warning('Please enter your reply');
      return;
    }

    try {
      setSending(true);
      await chatAPI.sendHumanMessage({
        conversation_id: handoff.conversation_id,
        content: replyContent,
        agent_name: agentName || 'Human Support'
      });

      antMessage.success('Reply sent successfully');
      setReplyContent('');

      // Refresh conversation
      await fetchHandoffDetail();
    } catch (error) {
      console.error('Failed to send:', error);
      antMessage.error('Failed to send');
    } finally {
      setSending(false);
    }
  };

  const showTakeoverModal = () => {
    setTempAgentName(agentName || 'Sales-John Doe');
    setTakeoverModalVisible(true);
  };

  const handleTakeOver = async () => {
    if (!tempAgentName.trim()) {
      antMessage.warning('Please enter your name');
      return;
    }

    try {
      setTakeoverModalVisible(false);
      await chatAPI.updateHandoffStatus(handoffId, {
        status: 'processing',
        agent_name: tempAgentName
      });

      setAgentName(tempAgentName);
      antMessage.success(`${tempAgentName} has taken over the conversation`);

      // Send browser notification
      if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('Handoff Taken Over', {
          body: `${tempAgentName} has taken over the conversation`,
          icon: '/logo.png'
        });
      }

      await fetchHandoffDetail();
    } catch (error) {
      console.error('Failed to take over:', error);
      antMessage.error('Failed to take over');
    }
  };

  // Request notification permission
  useEffect(() => {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }, []);

  const handleComplete = async () => {
    try {
      await chatAPI.updateHandoffStatus(handoffId, {
        status: 'completed'
      });

      antMessage.success('Service completed');
      navigate('/admin/handoffs');
    } catch (error) {
      console.error('Failed to complete:', error);
      antMessage.error('Failed to complete');
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 100 }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!handoff) {
    return <Empty description="Handoff record does not exist" />;
  }

  const getSenderIcon = (sender) => {
    if (sender === 'customer') return <UserOutlined style={{ fontSize: 16 }} />;
    if (sender === 'human') return <UserSwitchOutlined style={{ fontSize: 16 }} />;
    return <RobotOutlined style={{ fontSize: 16 }} />;
  };

  const getSenderColor = (sender) => {
    if (sender === 'customer') return 'blue';
    if (sender === 'human') return 'purple';
    return 'green';
  };

  const getSenderText = (sender) => {
    if (sender === 'customer') return 'Customer';
    if (sender === 'human') return 'Human';
    return 'AI';
  };

  return (
    <div style={{ padding: 24 }}>
      <Button
        icon={<ArrowLeftOutlined />}
        onClick={() => navigate('/admin/handoffs')}
        style={{ marginBottom: 16 }}
      >
        Back to Handoff Queue
      </Button>

      {/* Customer and Handoff Info */}
      <Card title="Handoff Information" style={{ marginBottom: 24 }}>
        <Descriptions>
          <Descriptions.Item label="Customer Name">
            <strong>{customer.name}</strong>
          </Descriptions.Item>
          <Descriptions.Item label="Customer Email">{customer.email}</Descriptions.Item>
          <Descriptions.Item label="Priority">
            <Tag color={customer.priority_score >= 4 ? 'red' : 'blue'}>
              {customer.priority_score} Score
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Handoff Reason">{handoff.trigger_reason}</Descriptions.Item>
          <Descriptions.Item label="Status">
            <Tag color={handoff.status === 'completed' ? 'green' : 'orange'}>
              {handoff.status}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Agent Name">{handoff.agent_name || '-'}</Descriptions.Item>
        </Descriptions>
      </Card>

      {/* Conversation History */}
      <Card
        title="Conversation History"
        extra={
          <Space>
            {handoff.status === 'pending' && (
              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                onClick={showTakeoverModal}
              >
                Take Over Conversation
              </Button>
            )}
            {handoff.status === 'processing' && (
              <Button
                type="primary"
                icon={<CheckCircleOutlined />}
                onClick={handleComplete}
              >
                Complete Service
              </Button>
            )}
          </Space>
        }
      >
        {conversations.length === 0 ? (
          <Empty description="No conversation history yet" />
        ) : (
          conversations.map((conversation) => (
            <div key={conversation.id} style={{ marginBottom: 32 }}>
              <Timeline>
                {conversation.messages && conversation.messages.map((message) => (
                  <Timeline.Item
                    key={message.id}
                    dot={getSenderIcon(message.sender.toLowerCase())}
                    color={getSenderColor(message.sender.toLowerCase())}
                  >
                    <div className={styles.messageItem}>
                      <div className={styles.messageHeader}>
                        <Tag color={getSenderColor(message.sender.toLowerCase())}>
                          {getSenderText(message.sender.toLowerCase())}
                        </Tag>
                        <span className={styles.messageTime}>
                          {message.created_at}
                        </span>
                        {message.ai_confidence !== undefined && (
                          <Tag>Confidence: {(message.ai_confidence * 100).toFixed(0)}%</Tag>
                        )}
                      </div>
                      <div className={styles.messageContent}>
                        {message.sender.toLowerCase() !== 'customer' ? (
                          <ReactMarkdown>{message.content}</ReactMarkdown>
                        ) : (
                          <p>{message.content}</p>
                        )}
                      </div>
                    </div>
                  </Timeline.Item>
                ))}
              </Timeline>
            </div>
          ))
        )}
      </Card>

      {/* Human Reply Panel */}
      {handoff.status !== 'completed' && (
        <>
          <Divider />
          <Card title="Human Reply" size="small">
            <Space direction="vertical" style={{ width: '100%' }}>
              <TextArea
                value={replyContent}
                onChange={(e) => setReplyContent(e.target.value)}
                placeholder="Enter your reply..."
                rows={4}
                disabled={sending}
              />
              <div style={{ textAlign: 'right' }}>
                <Button
                  type="primary"
                  icon={<SendOutlined />}
                  onClick={handleSendReply}
                  loading={sending}
                  disabled={!replyContent.trim()}
                >
                  Send Reply
                </Button>
              </div>
            </Space>
          </Card>
        </>
      )}

      {/* Take Over Modal */}
      <Modal
        title="Take Over Conversation"
        open={takeoverModalVisible}
        onOk={handleTakeOver}
        onCancel={() => setTakeoverModalVisible(false)}
        okText="Confirm Take Over"
        cancelText="Cancel"
      >
        <Input
          placeholder="Please enter your name"
          value={tempAgentName}
          onChange={(e) => setTempAgentName(e.target.value)}
          onPressEnter={handleTakeOver}
          autoFocus
        />
      </Modal>
    </div>
  );
};

export default HandoffDetail;
