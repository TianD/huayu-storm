import React, { Component } from 'react';
import './App.css';
import { Layout, Menu } from 'antd';
import Overview from './components/Overview';
import Logo from './logo.png';

const { Header, Content, Footer } = Layout;

class App extends Component {

    constructor() {
        super()
        this.state = {
            page: '1',
        }
    }

    onChange(event) {
        this.setState(
            { page: event.key }
        )
    }

    render() {
        let current_key = this.state.page;
        let current_page;
        switch (current_key) {
            case "1":
                current_page = <Overview />
                break
            case "2":
                current_page = <div />
                break
            case "3":
                current_page = <div />
                break
            case "4":
                current_page = <div />
                break
            default:
                current_page = <Overview />
        }

        return (
            <div className="App">
                <Layout className="layout">
                    <Header>
                        <div className="logo" />

                        <Menu
                            theme="dark"
                            mode="horizontal"
                            defaultSelectedKeys={[current_key]}
                            style={{ lineHeight: '64px' }}
                            onClick={(value) => this.onChange(value)}
                        >
                            <Menu.Item key="1">Compositing</Menu.Item>
                            <Menu.Item key="2">Maya批处理</Menu.Item>
                            <Menu.Item key="3">Nuke模板</Menu.Item>
                            <Menu.Item key="4">序列转视频</Menu.Item>
                        </Menu>
                    </Header>
                    <Content style={{ padding: '20px 50px' }}>
                        <div className="site-layout-content">
                            {current_page}
                        </div>
                    </Content>
                    <Footer style={{ textAlign: 'center' }}><img src={Logo} height="10%" width="10%" alt="" /></Footer>
                </Layout>
            </div>
        );
    }

}

export default App;
