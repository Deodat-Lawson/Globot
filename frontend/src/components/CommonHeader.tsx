import React from 'react';
import { SignedIn, SignedOut, UserButton, useClerk, useUser } from '@clerk/clerk-react';
import { Shield, Menu as MenuIcon } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Dropdown, MenuProps } from 'antd';

export const CommonHeader: React.FC = () => {
    const navigate = useNavigate();
    const { openSignIn } = useClerk();
    const { user } = useUser();

    const userEmail = user?.primaryEmailAddress?.emailAddress?.toLowerCase();
    const whitelistStr = import.meta.env.VITE_ADMIN_WHITELIST || '';
    const adminWhitelist = whitelistStr.split(',').map((e: string) => e.trim().toLowerCase());

    const isAdmin =
        user?.publicMetadata?.role === 'admin' ||
        (userEmail && adminWhitelist.includes(userEmail));

    const adminMenuItems: MenuProps['items'] = [
        {
            key: 'dashboard',
            label: '管理控制台',
            onClick: () => navigate('/admin'),
        },
        {
            key: 'customers',
            label: '客户档案管理',
            onClick: () => navigate('/admin'), // In MVP, pointing to same place
        },
        {
            key: 'ai-logs',
            label: 'AI 决策日志',
            disabled: true,
        },
        {
            type: 'divider',
        },
        {
            key: 'settings',
            label: '系统设置',
            disabled: true,
        },
    ];

    return (
        <header style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '0 20px',
            height: '56px',
            background: '#0f1621',
            borderBottom: '1px solid #1a2332',
            zIndex: 1000, // Ensure header is above everything
            position: 'relative'
        }}>
            <div
                style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }}
                onClick={() => navigate('/pay')}
            >
                <div style={{
                    width: '32px',
                    height: '32px',
                    background: 'linear-gradient(135deg, #0078d4 0%, #4a90e2 100%)',
                    borderRadius: '4px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                }}>
                    <Shield style={{ width: '20px', height: '20px', color: 'white' }} />
                </div>
                <h3 style={{ color: 'white', margin: 0, fontSize: '1.1rem', fontWeight: 600 }}>Globot AI</h3>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <SignedIn>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        {isAdmin && (
                            <Dropdown menu={{ items: adminMenuItems }} placement="bottomRight" arrow>
                                <div style={{
                                    cursor: 'pointer',
                                    color: 'white',
                                    display: 'flex',
                                    alignItems: 'center',
                                    padding: '4px'
                                }}>
                                    <MenuIcon style={{ width: '20px', height: '20px' }} />
                                </div>
                            </Dropdown>
                        )}
                        <UserButton afterSignOutUrl="/pay" />
                    </div>
                </SignedIn>
                <SignedOut>
                    <button
                        onClick={() => openSignIn()}
                        style={{
                            padding: '6px 16px',
                            background: '#0078d4',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            fontSize: '0.875rem',
                            fontWeight: 500,
                            cursor: 'pointer',
                            transition: 'background 0.2s'
                        }}
                        onMouseOver={(e) => (e.currentTarget.style.background = '#005a9e')}
                        onMouseOut={(e) => (e.currentTarget.style.background = '#0078d4')}
                    >
                        Login
                    </button>
                </SignedOut>
            </div>
        </header>
    );
};
