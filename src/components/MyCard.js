import React, { Component } from 'react';
import { Card } from 'antd';


const { Meta } = Card;

class MyCard extends Component {
    render() {
        return (
            <Card
                hoverable
                style={{ width: 240 , margin: (10,10,10,10)}}
                cover={<img alt="example" src="https://gw.alipayobjects.com/zos/rmsportal/JiqGstEfoWAOHiTxclqi.png" />}
                onClick={(event)=>this.props.onClick(event)}
            >
                <Meta title="Europe Street beat" description="www.instagram.com" />
            </Card>
        )
    }
}

export default MyCard